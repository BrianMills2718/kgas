"""Simple table storage service"""
import sqlite3
import json
from typing import Dict, Any, List

class TableService:
    """Simple table storage service"""
    
    def __init__(self, db_path: str = 'vertical_slice.db'):
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """Create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS vs2_embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS vs2_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def save_embedding(self, text: str, embedding: list) -> int:
        """Save an embedding"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'INSERT INTO vs2_embeddings (text, embedding) VALUES (?, ?)',
                (text, json.dumps(embedding))
            )
            return cursor.lastrowid
    
    def save_data(self, key: str, value: Any) -> int:
        """Save arbitrary data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'INSERT INTO vs2_data (key, value) VALUES (?, ?)',
                (key, json.dumps(value))
            )
            return cursor.lastrowid
    
    def get_embeddings(self, limit: int = 10) -> List[Dict]:
        """Get recent embeddings"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                'SELECT * FROM vs2_embeddings ORDER BY id DESC LIMIT ?',
                (limit,)
            ).fetchall()
            return [dict(row) for row in rows]