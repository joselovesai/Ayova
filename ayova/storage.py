"""SQLite storage for encrypted messages - AYOVA edition"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict


class MessageStore:
    """SQLite-based encrypted message storage for AYOVA"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            ayova_dir = Path.home() / ".ayova"
            ayova_dir.mkdir(exist_ok=True)
            db_path = ayova_dir / "messages.db"
        self.db_path = str(db_path)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    encrypted_data BLOB NOT NULL,
                    salt BLOB NOT NULL,
                    tag TEXT DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tag ON messages(tag)
            """)
            conn.commit()
    
    def save_message(self, encrypted_data: bytes, salt: bytes, tag: str = "general") -> int:
        """Save encrypted message, return message ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO messages (encrypted_data, salt, tag) VALUES (?, ?, ?)",
                (encrypted_data, salt, tag)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_messages(self, tag: Optional[str] = None) -> List[Dict]:
        """Retrieve encrypted messages (without decrypting)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if tag:
                rows = conn.execute(
                    "SELECT id, encrypted_data, salt, tag, created_at FROM messages WHERE tag = ? ORDER BY created_at DESC",
                    (tag,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, encrypted_data, salt, tag, created_at FROM messages ORDER BY created_at DESC"
                ).fetchall()
            return [dict(row) for row in rows]
    
    def get_message_by_id(self, msg_id: int) -> Optional[Dict]:
        """Get single message by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT id, encrypted_data, salt, tag, created_at FROM messages WHERE id = ?",
                (msg_id,)
            ).fetchone()
            return dict(row) if row else None
    
    def delete_message(self, msg_id: int) -> bool:
        """Delete message by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_tags(self) -> List[str]:
        """Get all unique tags"""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT DISTINCT tag FROM messages ORDER BY tag").fetchall()
            return [row[0] for row in rows]
    
    def count_messages(self, tag: Optional[str] = None) -> int:
        """Count messages (optionally by tag)"""
        with sqlite3.connect(self.db_path) as conn:
            if tag:
                result = conn.execute(
                    "SELECT COUNT(*) FROM messages WHERE tag = ?", (tag,)
                ).fetchone()
            else:
                result = conn.execute("SELECT COUNT(*) FROM messages").fetchone()
            return result[0] if result else 0
