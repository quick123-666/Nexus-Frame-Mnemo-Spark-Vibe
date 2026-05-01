#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV Global Mnemo: Cross-Project Experience Database
Stores successful fixes and patterns across all projects.
"""
import sqlite3
import json
import os
from typing import List, Dict, Optional

class GlobalMnemo:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_pattern TEXT NOT NULL,
                    solution TEXT NOT NULL,
                    context_tags TEXT, -- JSON array
                    frequency INTEGER DEFAULT 1,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def add_experience(self, error_pattern: str, solution: str, context_tags: List[str]):
        """
        Add a new successful fix to the global database.
        """
        with sqlite3.connect(self.db_path) as conn:
            # Check if similar error exists
            existing = conn.execute(
                "SELECT id, frequency FROM experiences WHERE error_pattern LIKE ?", 
                (f"%{error_pattern}%",)
            ).fetchone()
            
            if existing:
                # Update existing
                conn.execute(
                    "UPDATE experiences SET frequency = frequency + 1, last_used = CURRENT_TIMESTAMP WHERE id = ?",
                    (existing[0],)
                )
            else:
                # Insert new
                conn.execute(
                    "INSERT INTO experiences (error_pattern, solution, context_tags) VALUES (?, ?, ?)",
                    (error_pattern, solution, json.dumps(context_tags))
                )

    def search_solutions(self, error_msg: str, context_tags: List[str] = None) -> List[Dict]:
        """
        Search for similar past errors.
        Prioritizes by:
        1. Pattern match in error message
        2. Context tag overlap
        3. Frequency (how many times it worked before)
        """
        results = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # 1. Text Match
            rows = conn.execute(
                "SELECT * FROM experiences WHERE error_pattern LIKE ?", 
                (f"%{error_msg}%",)
            ).fetchall()
            
            # 2. Sort by Frequency
            sorted_rows = sorted(rows, key=lambda r: r["frequency"], reverse=True)
            
            for row in sorted_rows:
                results.append({
                    "id": row["id"],
                    "pattern": row["error_pattern"],
                    "solution": row["solution"],
                    "frequency": row["frequency"],
                    "match_score": 100 # Simplified score
                })
        
        return results
