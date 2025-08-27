#!/usr/bin/env python3
"""
Enhanced ProvenanceService with uncertainty tracking
Builds on existing ProvenanceService
"""

import sqlite3
import json
import time
from typing import Dict, Any, List
from datetime import datetime

class ProvenanceEnhanced:
    """Track operations with uncertainty and construct mapping"""
    
    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path
        self._setup_database()
    
    def _setup_database(self):
        """Create provenance tables with uncertainty fields"""
        conn = sqlite3.connect(self.sqlite_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vs_provenance (
                operation_id TEXT PRIMARY KEY,
                tool_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                inputs TEXT,
                outputs TEXT,
                uncertainty REAL,
                reasoning TEXT,
                construct_mapping TEXT,
                execution_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def track_operation(self, 
                       tool_id: str,
                       operation: str,
                       inputs: Dict,
                       outputs: Dict,
                       uncertainty: float,
                       reasoning: str,
                       construct_mapping: str) -> str:
        """
        Track operation with uncertainty and construct mapping
        """
        import uuid
        operation_id = f"op_{uuid.uuid4().hex[:12]}"
        
        conn = sqlite3.connect(self.sqlite_path)
        conn.execute("""
            INSERT INTO vs_provenance 
            (operation_id, tool_id, operation, inputs, outputs, 
             uncertainty, reasoning, construct_mapping, execution_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            operation_id,
            tool_id,
            operation,
            json.dumps(inputs),
            json.dumps(outputs),
            uncertainty,
            reasoning,
            construct_mapping,
            time.time()
        ))
        conn.commit()
        conn.close()
        
        return operation_id
    
    def get_operation_chain(self, final_operation_id: str) -> List[Dict]:
        """Get all operations leading to a result"""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.execute("""
            SELECT * FROM vs_provenance 
            WHERE created_at <= (
                SELECT created_at FROM vs_provenance 
                WHERE operation_id = ?
            )
            ORDER BY created_at
        """, (final_operation_id,))
        
        operations = []
        for row in cursor:
            operations.append({
                'operation_id': row[0],
                'tool_id': row[1],
                'operation': row[2],
                'uncertainty': row[5],
                'reasoning': row[6],
                'construct_mapping': row[7]
            })
        
        conn.close()
        return operations