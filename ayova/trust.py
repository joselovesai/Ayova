"""Trust management - B must trust A before A can message B"""
import json
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict
import base64


class TrustManager:
    """Manages trusted contacts - whitelist-based messaging"""
    
    def __init__(self):
        self.db_path = Path.home() / ".ayova" / "trust.db"
        self._init_db()
    
    def _init_db(self):
        """Initialize trust database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trusted (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    public_key BLOB NOT NULL,
                    device_id TEXT,
                    fingerprint TEXT,
                    trusted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    can_send BOOLEAN DEFAULT 1,
                    notes TEXT
                )
            """)
            conn.commit()
    
    def trust(self, username: str, public_key: str, device_id: str = None, 
              fingerprint: str = None, notes: str = None) -> bool:
        """Add a trusted contact"""
        try:
            pubkey_bytes = base64.b64decode(public_key)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO trusted 
                       (username, public_key, device_id, fingerprint, notes) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (username, pubkey_bytes, device_id, fingerprint, notes)
                )
                conn.commit()
            return True
        except Exception as e:
            return False
    
    def untrust(self, username: str) -> bool:
        """Remove trust from a contact"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM trusted WHERE username = ?", (username,))
            conn.commit()
            return cursor.rowcount > 0
    
    def is_trusted(self, username: str) -> bool:
        """Check if a username is trusted"""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                "SELECT 1 FROM trusted WHERE username = ?", (username,)
            ).fetchone()
            return result is not None
    
    def get_trusted(self, username: str) -> Optional[Dict]:
        """Get trusted contact details"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM trusted WHERE username = ?", (username,)
            ).fetchone()
            if row:
                return {
                    'username': row['username'],
                    'public_key': base64.b64encode(row['public_key']).decode(),
                    'device_id': row['device_id'],
                    'fingerprint': row['fingerprint'],
                    'trusted_at': row['trusted_at']
                }
            return None
    
    def list_trusted(self) -> List[Dict]:
        """List all trusted contacts"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM trusted ORDER BY trusted_at DESC"
            ).fetchall()
            return [
                {
                    'username': r['username'],
                    'fingerprint': r['fingerprint'],
                    'trusted_at': r['trusted_at']
                }
                for r in rows
            ]
    
    def can_receive_from(self, username: str, public_key: bytes) -> bool:
        """Verify if message from username with public_key should be accepted"""
        trusted = self.get_trusted(username)
        if not trusted:
            return False
        # Verify public key matches
        expected_key = base64.b64decode(trusted['public_key'])
        return expected_key == public_key


# Global instance
_trust_manager = None

def get_trust_manager() -> TrustManager:
    """Get or create global trust manager"""
    global _trust_manager
    if _trust_manager is None:
        _trust_manager = TrustManager()
    return _trust_manager
