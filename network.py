"""Lightweight P2P networking with asyncssh - Light Hybrid mode with auto port forwarding"""
import asyncio
import asyncssh
import json
from pathlib import Path
from typing import Optional, Callable, Dict
from .identity import get_identity
from .trust import get_trust_manager
from .upnp import ensure_port_forwarded, check_port_forward


# Global connection pool (max 3 to save RAM)
_connections: Dict[str, asyncssh.SSHClientConnection] = {}
MAX_CONNECTIONS = 3
_port_forwarded = False  # Track if we've already tried port forwarding


class AyovaNetwork:
    """Client-only P2P networking with automatic port forwarding"""
    
    def __init__(self):
        self.identity = get_identity()
        self.trust = get_trust_manager()
        self.known_hosts_file = Path.home() / ".ayova" / "known_hosts"
    
    def ensure_port_open(self, port: int = 23231, silent: bool = False) -> bool:
        """Ensure port is forwarded using UPnP (auto on first use)"""
        global _port_forwarded
        
        if _port_forwarded:
            return True  # Already tried, don't spam
        
        success, message = ensure_port_forwarded(port, silent=silent)
        _port_forwarded = True
        
        return success
    
    async def connect(self, host: str, port: int = 22, username: str = None) -> Optional[asyncssh.SSHClientConnection]:
        """Connect to a peer via SSH (client-only, outbound)"""
        if not self.identity.exists():
            return None
        
        conn_key = f"{host}:{port}"
        
        # Return existing connection if healthy
        if conn_key in _connections:
            conn = _connections[conn_key]
            if not conn.is_closed():
                return conn
            del _connections[conn_key]
        
        # Enforce connection limit
        if len(_connections) >= MAX_CONNECTIONS:
            # Close oldest connection
            oldest = next(iter(_connections))
            _connections[oldest].close()
            del _connections[oldest]
        
        try:
            # Connect without host key checking (we use E2E crypto anyway)
            conn = await asyncssh.connect(
                host,
                port=port,
                username=username or "ayova",
                known_hosts=None,  # We verify via E2E, not SSH host keys
                connect_timeout=10,
                keepalive_interval=30,
                compression_algs=['zlib@openssh.com', 'zlib', 'none']  # Save bandwidth
            )
            _connections[conn_key] = conn
            return conn
        except Exception as e:
            return None
    
    async def send_message(self, host: str, encrypted_payload: bytes, 
                          recipient_username: str, port: int = 22) -> bool:
        """Send encrypted message to a peer"""
        conn = await self.connect(host, port)
        if not conn:
            return False
        
        try:
            # Create protocol envelope
            envelope = {
                'sender': self.identity.username,
                'sender_pubkey': self.identity.get_public_identity()['public_key'],
                'recipient': recipient_username,
                'payload': encrypted_payload.hex(),
                'protocol': 'ayova-p2p-v1'
            }
            
            # Open channel and send
            async with conn.create_tcp_channel('ayova', 0) as channel:
                channel.write(json.dumps(envelope).encode())
                channel.write_eof()
                return True
        except Exception:
            return False
    
    async def direct_tcp_send(self, host: str, port: int, encrypted_payload: bytes,
                              recipient_username: str) -> bool:
        """Lightweight direct TCP send (no SSH overhead)"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=10
            )
            
            envelope = {
                'sender': self.identity.username,
                'sender_pubkey': self.identity.get_public_identity()['public_key'],
                'recipient': recipient_username,
                'payload': encrypted_payload.hex(),
                'protocol': 'ayova-p2p-v1-tcp'
            }
            
            data = json.dumps(envelope).encode()
            writer.write(len(data).to_bytes(4, 'big'))  # 4-byte length prefix
            writer.write(data)
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            return False
    
    def close_all(self):
        """Close all connections to free RAM"""
        for conn in _connections.values():
            conn.close()
        _connections.clear()


# Global instance
_network = None

def get_network() -> AyovaNetwork:
    """Get or create network instance"""
    global _network
    if _network is None:
        _network = AyovaNetwork()
    return _network


async def send_to_peer(username: str, host: str, encrypted_payload: bytes, 
                       use_ssh: bool = True, port: int = None) -> bool:
    """High-level send function with auto port forwarding check"""
    net = get_network()
    
    # Auto-try port forwarding on first send (so we can receive replies!)
    net.ensure_port_open(23231, silent=True)
    
    if use_ssh:
        return await net.send_message(host, encrypted_payload, username, port or 22)
    else:
        return await net.direct_tcp_send(host, port or 23231, encrypted_payload, username)
