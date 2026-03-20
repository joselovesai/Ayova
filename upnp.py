"""Automatic UPnP port forwarding for AYOVA P2P"""
import socket
from typing import Optional, Tuple


def get_local_ip() -> str:
    """Get local IP address"""
    try:
        # Connect to a public DNS to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def auto_port_forward(port: int = 23231, protocol: str = 'TCP', 
                      duration: int = 3600) -> Tuple[bool, str]:
    """
    Automatically forward a port using UPnP
    
    Args:
        port: Port to forward (default 23231 for AYOVA)
        protocol: 'TCP' or 'UDP'
        duration: How long to keep port open (seconds)
    
    Returns:
        (success: bool, message: str)
    """
    try:
        import miniupnpc
        
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 200  # ms
        
        # Discover UPnP devices
        num_devices = upnp.discover()
        if num_devices == 0:
            return False, "No UPnP devices found (router may have UPnP disabled)"
        
        # Select internet gateway device
        try:
            upnp.selectigd()
        except Exception as e:
            return False, f"Could not select gateway: {str(e)}"
        
        # Get external IP
        external_ip = upnp.externalipaddress()
        local_ip = get_local_ip()
        
        # Check if port is already mapped
        existing_mapping = upnp.getspecificportmapping(port, protocol)
        if existing_mapping is not None:
            # Port already forwarded, could be us or someone else
            return True, f"Port {port} already forwarded (external IP: {external_ip})"
        
        # Add port mapping
        result = upnp.addportmapping(
            port,           # external port
            protocol,       # protocol
            local_ip,       # internal host
            port,           # internal port
            'AYOVA P2P Messenger',  # description
            '',             # remote host (empty = any)
            duration        # lease duration (0 = permanent on some routers)
        )
        
        if result:
            return True, f"✓ Port {port} forwarded! External IP: {external_ip} (share this with friends)"
        else:
            return False, "Router rejected port forwarding request"
            
    except ImportError:
        return False, "miniupnpc not installed (run: pip3 install miniupnpc)"
    except Exception as e:
        return False, f"UPnP error: {str(e)}"


def remove_port_forward(port: int = 23231, protocol: str = 'TCP') -> bool:
    """Remove a port forwarding mapping"""
    try:
        import miniupnpc
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 200
        
        if upnp.discover() > 0:
            upnp.selectigd()
            upnp.deleteportmapping(port, protocol)
            return True
    except Exception:
        pass
    return False


def check_port_forward(port: int = 23231) -> Tuple[bool, Optional[str]]:
    """Check if port is forwarded and get external IP"""
    try:
        import miniupnpc
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 200
        
        if upnp.discover() > 0:
            upnp.selectigd()
            external_ip = upnp.externalipaddress()
            
            # Check if our port is mapped
            mapping = upnp.getspecificportmapping(port, 'TCP')
            if mapping:
                return True, external_ip
            return False, external_ip
            
    except Exception:
        pass
    return False, None


# Convenience function for AYOVA integration
def ensure_port_forwarded(port: int = 23231, silent: bool = False) -> Tuple[bool, str]:
    """
    Ensure port is forwarded, trying automatic UPnP first
    
    Args:
        port: Port to ensure is forwarded
        silent: If True, don't print status messages
    
    Returns:
        (success, message)
    """
    success, message = auto_port_forward(port)
    
    if not silent:
        if success:
            print(f"ℹ {message}")
        else:
            print(f"⚠ Auto port forward failed: {message}")
            print(f"⚠ Manual forwarding needed: Forward port {port} to your local IP")
    
    return success, message
