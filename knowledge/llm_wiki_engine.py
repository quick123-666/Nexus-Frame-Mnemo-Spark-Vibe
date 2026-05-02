#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV LLM Wiki Engine: 动态知识存储与检索
允许 AI 在运行过程中学习新概念、保存经验并建立知识关联。
基于 SQLite + FTS5 实现。
"""
import sqlite3
import json
import os
from typing import List, Dict, Optional
from datetime import datetime

class LlmWikiEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库表"""
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            # 1. 主表：存储页面内容
            conn.execute("""
                CREATE TABLE IF NOT EXISTS wiki_pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL UNIQUE,
                    content TEXT NOT NULL,
                    tags TEXT DEFAULT '[]',
                    references TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 2. FTS5 虚拟表：用于全文检索
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS wiki_search 
                USING fts5(title, content, content='wiki_pages', content_rowid='id')
            """)
            conn.commit()

    def save_page(self, title: str, content: str, tags: List[str] = None):
        """保存或更新知识页面"""
        if tags is None: tags = []
        tags_json = json.dumps(tags, ensure_ascii=False)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 检查是否存在
            cursor.execute("SELECT id FROM wiki_pages WHERE title = ?", (title,))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute(
                    "UPDATE wiki_pages SET content = ?, tags = ?, updated_at = CURRENT_TIMESTAMP WHERE title = ?",
                    (content, tags_json, title)
                )
            else:
                cursor.execute(
                    "INSERT INTO wiki_pages (title, content, tags) VALUES (?, ?, ?)",
                    (title, content, tags_json)
                )
            
            # 同步更新 FTS5 索引
            try:
                conn.execute("INSERT INTO wiki_search(wiki_search) VALUES('rebuild')")
            except sqlite3.OperationalError:
                pass # Rebuild might fail if table is busy, handled by next insert
            
            # 触发器会自动更新 FTS5，如果有的话。这里我们手动 rebuild 最简单，或者使用 Triggers
            # FTS5 external content tables need triggers to stay in sync automatically.
            # To keep it simple, we rebuild on save or use triggers. 
            # Better approach for simple scripts: Triggers.
            
            # Add triggers if not exists
            self._ensure_triggers(conn)
            
            conn.commit()

    def _ensure_triggers(self, conn):
        """确保 FTS5 触发器存在"""
        try:
            # Insert trigger
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS wiki_pages_ai AFTER INSERT ON wiki_pages BEGIN
                    INSERT INTO wiki_search(rowid, title, content) VALUES (new.id, new.title, new.content);
                END
            """)
            # Update trigger
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS wiki_pages_au AFTER UPDATE ON wiki_pages BEGIN
                    DELETE FROM wiki_search WHERE docid=old.id;
                    INSERT INTO wiki_search(rowid, title, content) VALUES (new.id, new.title, new.content);
                END
            """)
            # Delete trigger
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS wiki_pages_ad AFTER DELETE ON wiki_pages BEGIN
                    DELETE FROM wiki_search WHERE docid=old.id;
                END
            """)
        except sqlite3.OperationalError:
            pass

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """基于 FTS5 的全文检索"""
        results = []
        with sqlite3.connect(self.db_path) as conn:
            try:
                # 使用 FTS5 进行排名检索
                rows = conn.execute(
                    "SELECT p.id, p.title, p.content, p.tags, rank FROM wiki_search s "
                    "JOIN wiki_pages p ON s.rowid = p.id "
                    "WHERE wiki_search MATCH ? "
                    "ORDER BY rank LIMIT ?",
                    (query, limit)
                ).fetchall()
                
                for row in rows:
                    results.append({
                        "id": row[0],
                        "title": row[1],
                        "content": row[2],
                        "tags": json.loads(row[3]),
                        "score": row[4]
                    })
            except sqlite3.OperationalError:
                # Fallback to LIKE if FTS5 fails
                rows = conn.execute(
                    "SELECT id, title, content, tags FROM wiki_pages "
                    "WHERE content LIKE ? OR title LIKE ? LIMIT ?",
                    (f"%{query}%", f"%{query}%", limit)
                ).fetchall()
                for row in rows:
                    results.append({
                        "id": row[0],
                        "title": row[1],
                        "content": row[2],
                        "tags": json.loads(row[3]),
                        "score": 0
                    })
        return results

    def get_page(self, title: str) -> Optional[Dict]:
        """获取特定页面"""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM wiki_pages WHERE title = ?", (title,)).fetchone()
            if row:
                return {
                    "id": row[0],
                    "title": row[1],
                    "content": row[2],
                    "tags": json.loads(row[3]),
                    "created_at": row[5]
                }
        return None

    def list_pages(self, tag: str = None) -> List[Dict]:
        """列出所有页面，可选按标签过滤"""
        results = []
        with sqlite3.connect(self.db_path) as conn:
            if tag:
                # SQLite doesn't support easy JSON querying in older versions,
                # but we can use LIKE for simplicity here.
                rows = conn.execute(
                    "SELECT * FROM wiki_pages WHERE tags LIKE ?", 
                    (f"%\"{tag}\"%",)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM wiki_pages").fetchall()
            
            for row in rows:
                results.append({
                    "id": row[0],
                    "title": row[1],
                    "content_snippet": row[2][:100] + "...",
                    "tags": json.loads(row[3])
                })
        return results

    def delete_page(self, title: str):
        """删除页面"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM wiki_pages WHERE title = ?", (title,))
            conn.commit()
