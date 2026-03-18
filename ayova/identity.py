"""Device-based identity with Ed25519 keys - AYOVA P2P"""
import os
import json
import base64
from pathlib import Path
from typing import Optional, Dict
import nacl.signing
import nacl.encoding


class Identity:
    """Device-based identity: one device = one account"""
    
    def __init__(self):
        self.key_dir = Path.home() / ".ayova" / "identity"
        self.key_file = self.key_dir / "keys.json"
        self.username: Optional[str] = None
        self.signing_key: Optional[nacl.signing.SigningKey] = None
        self.verify_key: Optional[nacl.signing.VerifyKey] = None
        self.device_id: Optional[str] = None
        self._load()
    
    def _load(self):
        """Load existing identity or mark as new"""
        if self.key_file.exists():
            try:
                with open(self.key_file, 'r') as f:
                    data = json.load(f)
                self.username = data.get('username')
                self.device_id = data.get('device_id')
                # Decode private key
                seed = base64.b64decode(data['private_key'])
                self.signing_key = nacl.signing.SigningKey(seed)
                self.verify_key = self.signing_key.verify_key
            except Exception:
                pass  # Will trigger setup
    
    def exists(self) -> bool:
        """Check if identity already created"""
        return self.username is not None and self.signing_key is not None
    
    def create(self, username: str) -> Dict:
        """Create new identity with Ed25519 keypair"""
        self.username = username
        self.device_id = base64.b32encode(os.urandom(10)).decode().lower()[:16]
        
        # Generate Ed25519 keypair
        self.signing_key = nacl.signing.SigningKey.generate()
        self.verify_key = self.signing_key.verify_key
        
        # Save to disk
        self.key_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self.key_dir, 0o700)  # Secure permissions
        
        data = {
            'username': username,
            'device_id': self.device_id,
            'private_key': base64.b64encode(bytes(self.signing_key)).decode(),
            'public_key': base64.b64encode(bytes(self.verify_key)).decode(),
            'created_at': str(Path.home().stat().st_ctime)
        }
        
        with open(self.key_file, 'w') as f:
            json.dump(data, f, indent=2)
        os.chmod(self.key_file, 0o600)  # Secure permissions
        
        return self.get_public_identity()
    
    def get_public_identity(self) -> Dict:
        """Get public identity info (shareable)"""
        if not self.exists():
            return {}
        return {
            'username': self.username,
            'device_id': self.device_id,
            'public_key': base64.b64encode(bytes(self.verify_key)).decode(),
            'fingerprint': self.get_fingerprint()
        }
    
    def get_fingerprint(self) -> str:
        """Human-readable key fingerprint (emoji style)"""
        if not self.verify_key:
            return ""
        key_bytes = bytes(self.verify_key)
        # Use first 8 bytes to generate emoji fingerprint
        emojis = ["🦁", "🦊", "🐼", "🐨", "🐯", "🐷", "🐸", "🐙"]
        fingerprint = "".join(emojis[b % len(emojis)] for b in key_bytes[:8])
        return f"{fingerprint} {key_bytes[:4].hex().upper()}"
    
    def export_public_key(self) -> str:
        """Export public key in shareable format"""
        pub = self.get_public_identity()
        return json.dumps(pub, indent=2)
    
    def sign(self, message: bytes) -> bytes:
        """Sign message with Ed25519"""
        if not self.signing_key:
            raise RuntimeError("No identity created")
        return self.signing_key.sign(message).signature
    
    def verify(self, message: bytes, signature: bytes, pubkey: bytes) -> bool:
        """Verify signature with public key"""
        try:
            vk = nacl.signing.VerifyKey(pubkey)
            vk.verify(message, signature)
            return True
        except Exception:
            return False


# Global identity instance
_identity = None

def get_identity() -> Identity:
    """Get or create global identity instance"""
    global _identity
    if _identity is None:
        _identity = Identity()
    return _identity
