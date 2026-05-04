#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV Global Mnemo: Cross-Project Experience Database (Upgraded)
Features: FTS5 BM25 + Vector Search + RRF Fusion
"""
import sqlite3
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

try:
    from fastembed import TextEmbedding
    import numpy as np
    FASTEMBED_AVAILABLE = True
except ImportError:
    FASTEMBED_AVAILABLE = False
    np = None

class GlobalMnemo:
    """
    Cross-project experience database with hybrid search.
    
    Stores successful fixes/solutions and retrieves them via:
    - BM25 (FTS5): Keyword matching
    - Vector similarity: Semantic matching
    - RRF Fusion: Best of both worlds
    """
    
    def __init__(self, db_path: str, embedding_model: str = "BAAI/bge-small-en-v1.5"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.embedding_model = embedding_model
        self.embedder = None
        self.embedding_dim = 384
        
        # Initialize embedding model (graceful fallback if offline)
        if FASTEMBED_AVAILABLE:
            try:
                import os
                os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
                self.embedder = TextEmbedding(model_name=embedding_model, cache_dir="./models")
                self.embedding_dim = self.embedder._model.get_embedding_size()
                print(f"[GlobalMnemo] Embedder loaded: {embedding_model} (dim={self.embedding_dim})")
            except Exception as e:
                print(f"[GlobalMnemo] Note: Embedder unavailable ({e}), using BM25 only")
                self.embedder = None
        
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite with FTS5 and vector storage"""
        with sqlite3.connect(self.db_path) as conn:
            # Enable WAL mode
            conn.execute("PRAGMA journal_mode=WAL")
            
            # Main experiences table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_pattern TEXT NOT NULL,
                    solution TEXT NOT NULL,
                    context_tags TEXT,  -- JSON array
                    frequency INTEGER DEFAULT 1,
                    success_count INTEGER DEFAULT 1,
                    failure_count INTEGER DEFAULT 0,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    embedding BLOB,
                    metadata TEXT
                )
            """)
            
            # FTS5 virtual table for BM25 search
            try:
                conn.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS experiences_fts 
                    USING fts5(error_pattern, solution, content=experiences, content_rowid=id)
                """)
            except sqlite3.OperationalError:
                pass  # Already exists
            
            # Indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_frequency ON experiences(frequency DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_last_used ON experiences(last_used DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_success ON experiences(success_count DESC)")
            
            # Triggers to sync FTS5
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS exp_after_insert 
                AFTER INSERT ON experiences BEGIN
                    INSERT INTO experiences_fts(rowid, error_pattern, solution) 
                    VALUES (NEW.rowid, NEW.error_pattern, NEW.solution);
                END
            """)
            
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS exp_after_update 
                AFTER UPDATE OF error_pattern, solution ON experiences BEGIN
                    INSERT INTO experiences_fts(experiences_fts, rowid, error_pattern, solution) 
                    VALUES ('delete', OLD.rowid, OLD.error_pattern, OLD.solution);
                    INSERT INTO experiences_fts(rowid, error_pattern, solution) 
                    VALUES (NEW.rowid, NEW.error_pattern, NEW.solution);
                END
            """)
            
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS exp_after_delete 
                AFTER DELETE ON experiences BEGIN
                    INSERT INTO experiences_fts(experiences_fts, rowid, error_pattern, solution) 
                    VALUES ('delete', OLD.rowid, OLD.error_pattern, OLD.solution);
                END
            """)
    
    def _text_to_embedding(self, text: str) -> Optional[bytes]:
        """Convert text to embedding vector bytes"""
        if not self.embedder:
            return None
        try:
            embedding = list(self.embedder.embed([text]))[0]
            return embedding.astype(np.float32).tobytes()
        except Exception as e:
            print(f"[GlobalMnemo] Embedding error: {e}")
            return None
    
    def add_experience(self, error_pattern: str, solution: str, 
                       context_tags: List[str] = None, metadata: Dict = None):
        """
        Add a new successful fix to the global database.
        Uses UPSERT: updates frequency if error pattern exists.
        """
        with sqlite3.connect(self.db_path) as conn:
            # Check if similar error exists
            existing = conn.execute(
                "SELECT id, frequency FROM experiences WHERE error_pattern = ?", 
                (error_pattern,)
            ).fetchone()
            
            # Generate embedding
            embedding_blob = self._text_to_embedding(error_pattern + " " + solution)
            
            if existing:
                # Update existing: increment frequency and update solution
                conn.execute("""
                    UPDATE experiences 
                    SET frequency = frequency + 1,
                        solution = ?,
                        last_used = CURRENT_TIMESTAMP,
                        embedding = ?,
                        context_tags = ?
                    WHERE id = ?
                """, (solution, embedding_blob, 
                      json.dumps(context_tags or []), existing[0]))
            else:
                # Insert new
                conn.execute("""
                    INSERT INTO experiences 
                    (error_pattern, solution, context_tags, embedding, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (error_pattern, solution, 
                      json.dumps(context_tags or []), 
                      embedding_blob,
                      json.dumps(metadata or {})))
    
    def search_solutions(self, error_msg: str, context_tags: List[str] = None, 
                        limit: int = 5) -> List[Dict]:
        """
        Search for similar past errors using hybrid search.
        
        Prioritizes by:
        1. BM25 match in error message
        2. Vector similarity
        3. Frequency (how many times it worked before)
        4. Recency
        """
        # Get BM25 results
        bm25_results = self._search_bm25(error_msg, limit * 2)
        
        # Get vector results
        vector_results = self._search_vector(error_msg, limit * 2)
        
        # RRF fusion
        fused = self._rrf_fusion(bm25_results, vector_results)
        
        # Filter by context tags if provided
        if context_tags:
            fused = [r for r in fused if self._tags_overlap(json.loads(r.get('context_tags', '[]')), context_tags)]
        
        return fused[:limit]
    
    def _search_bm25(self, query: str, limit: int) -> List[Dict]:
        """FTS5 BM25 search (simplified, no bm25() function)"""
        results = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                # FTS5 query - simple OR query
                words = [w for w in query.split() if w]
                if not words:
                    return results
                
                fts_query = " OR ".join(words)
                
                rows = conn.execute("""
                    SELECT e.* 
                    FROM experiences e
                    JOIN experiences_fts ON e.rowid = experiences_fts.rowid
                    WHERE experiences_fts MATCH ?
                    LIMIT ?
                """, (fts_query, limit)).fetchall()
                
                for i, row in enumerate(rows):
                    results.append({
                        "id": row["id"],
                        "pattern": row["error_pattern"],
                        "solution": row["solution"],
                        "context_tags": row["context_tags"],
                        "frequency": row["frequency"],
                        "success_count": row["success_count"],
                        "score": len(rows) - i,  # Approximate rank score
                        "source": "bm25"
                    })
        except Exception as e:
            print(f"[GlobalMnemo] BM25 search error: {e}")
        
        return results
    
    def _search_vector(self, query: str, limit: int) -> List[Dict]:
        """Vector similarity search using cosine similarity"""
        if not self.embedder:
            return []
        
        results = []
        try:
            # Generate query embedding
            query_embedding = list(self.embedder.embed([query]))[0]
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute("""
                    SELECT id, error_pattern, solution, context_tags, 
                           frequency, success_count, embedding
                    FROM experiences
                    WHERE embedding IS NOT NULL
                """).fetchall()
                
                for row in rows:
                    if not row['embedding']:
                        continue
                    
                    doc_embedding = np.frombuffer(row['embedding'], dtype=np.float32)
                    
                    # Cosine similarity
                    dot = np.dot(query_embedding, doc_embedding)
                    norm_q = np.linalg.norm(query_embedding)
                    norm_d = np.linalg.norm(doc_embedding)
                    
                    if norm_q == 0 or norm_d == 0:
                        continue
                    
                    similarity = dot / (norm_q * norm_d)
                    
                    results.append({
                        "id": row["id"],
                        "pattern": row["error_pattern"],
                        "solution": row["solution"],
                        "context_tags": row["context_tags"],
                        "frequency": row["frequency"],
                        "success_count": row["success_count"],
                        "score": float(similarity),
                        "source": "vector"
                    })
                
                # Sort by similarity
                results.sort(key=lambda x: x['score'], reverse=True)
                results = results[:limit]
                
        except Exception as e:
            print(f"[GlobalMnemo] Vector search error: {e}")
        
        return results
    
    def _rrf_fusion(self, bm25_results: List[Dict], vector_results: List[Dict], 
                     k: int = 60) -> List[Dict]:
        """
        Reciprocal Rank Fusion (RRF) with weights
        
        Formula: score = 0.4/(k + rank_bm25) + 0.6/(k + rank_vector)
        """
        # Create rank dictionaries
        bm25_ranks = {r['id']: (i+1, r) for i, r in enumerate(bm25_results)}
        vector_ranks = {r['id']: (i+1, r) for i, r in enumerate(vector_results)}
        
        # Get all unique IDs
        all_ids = set(bm25_ranks.keys()) | set(vector_ranks.keys())
        
        fused = []
        for mid in all_ids:
            bm25_rank, bm25_data = bm25_ranks.get(mid, (None, None))
            vector_rank, vector_data = vector_ranks.get(mid, (None, None))
            
            # Calculate RRF score
            score = 0.0
            if bm25_rank:
                score += 0.4 / (k + bm25_rank)
            if vector_rank:
                score += 0.6 / (k + vector_rank)
            
            # Use the richer data source
            data = vector_data if vector_data else bm25_data
            if data:
                data['rrf_score'] = score
                data['bm25_rank'] = bm25_rank
                data['vector_rank'] = vector_rank
                # Combine scores
                data['score'] = score
                fused.append(data)
        
        # Sort by RRF score
        fused.sort(key=lambda x: x['score'], reverse=True)
        
        return fused
    
    def _tags_overlap(self, tags1_json: str, tags2: List[str]) -> bool:
        """Check if there's any overlap between two tag lists"""
        try:
            tags1 = json.loads(tags1_json) if tags1_json else []
            return bool(set(tags1) & set(tags2))
        except:
            return False
    
    def record_success(self, error_pattern: str):
        """Increment success count for an experience"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE experiences 
                SET success_count = success_count + 1,
                    last_used = CURRENT_TIMESTAMP
                WHERE error_pattern = ?
            """, (error_pattern,))
    
    def record_failure(self, error_pattern: str):
        """Increment failure count for an experience"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE experiences 
                SET failure_count = failure_count + 1
                WHERE error_pattern = ?
            """, (error_pattern,))
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            stats = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(frequency) as total_uses,
                    SUM(success_count) as total_successes,
                    SUM(failure_count) as total_failures,
                    AVG(frequency) as avg_frequency
                FROM experiences
            """).fetchone()
            
            return dict(stats) if stats else {}
