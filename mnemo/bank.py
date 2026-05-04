#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV Mnemo: Memory Bank Manager (Upgraded)
Features: FTS5 BM25 + Vector Search + RRF Fusion
"""
import os
import sqlite3
import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

try:
    from fastembed import TextEmbedding
    import numpy as np
    FASTEMBED_AVAILABLE = True
except ImportError:
    FASTEMBED_AVAILABLE = False
    np = None

class MemoryBank:
    """
    Upgraded Memory Bank with hybrid search (BM25 + Vector + RRF)
    
    Memory tiers:
    - core: Identity/persona (always loaded)
    - learned: Facts and knowledge
    - episodic: Session experiences
    - working: Temporary task context (auto-expires)
    - procedural: Behavioral rules
    """
    
    STANDARD_FILES = {
        "plan.md": "# Implementation Plan\n\n## Steps\n1. [ ] Step1\n",
        "progress.md": "# Progress\n\n## Completed\n- \n",
        "architecture.md": "# Architecture\n\n## Overview\n\n",
        "tech.md": "# Tech Stack\n\n## Dependencies\n\n",
    }
    
    def __init__(self, bank_path: str, embedding_model: str = "BAAI/bge-small-en-v1.5"):
        self.bank_path = Path(bank_path)
        self.bank_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.bank_path / "memory.db"
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
                print(f"[Mnemo] Embedder loaded: {embedding_model} (dim={self.embedding_dim})")
            except Exception as e:
                print(f"[Mnemo] Note: Embedder unavailable ({e}), using BM25 only")
                self.embedder = None
        
        self._initialize_db()
        self._initialize_bank()
    
    def _initialize_db(self):
        """Initialize SQLite with FTS5 and vector storage"""
        with sqlite3.connect(self.db_path) as conn:
            # Enable FTS5 extension
            conn.execute("PRAGMA journal_mode=WAL")
            
            # Main memories table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    tier TEXT NOT NULL DEFAULT 'learned',
                    content TEXT NOT NULL,
                    metadata TEXT,
                    importance REAL DEFAULT 0.5,
                    access_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    embedding BLOB
                )
            """)
            
            # FTS5 virtual table for BM25 search
            try:
                conn.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts 
                    USING fts5(content, content=memories, content_rowid=id)
                """)
            except sqlite3.OperationalError:
                pass  # Already exists
            
            # Indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tier ON memories(tier)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created ON memories(created_at DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance DESC)")
            
            # Trigger to sync FTS5 on insert
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS memories_after_insert 
                AFTER INSERT ON memories BEGIN
                    INSERT INTO memories_fts(rowid, content) VALUES (NEW.rowid, NEW.content);
                END
            """)
            
            # Trigger to sync FTS5 on update
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS memories_after_update 
                AFTER UPDATE OF content ON memories BEGIN
                    INSERT INTO memories_fts(memories_fts, rowid, content) 
                    VALUES ('delete', OLD.rowid, OLD.content);
                    INSERT INTO memories_fts(rowid, content) VALUES (NEW.rowid, NEW.content);
                END
            """)
            
            # Trigger to sync FTS5 on delete
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS memories_after_delete 
                AFTER DELETE ON memories BEGIN
                    INSERT INTO memories_fts(memories_fts, rowid, content) 
                    VALUES ('delete', OLD.rowid, OLD.content);
                END
            """)
    
    def _initialize_bank(self):
        """Initialize standard markdown files"""
        for filename, content in self.STANDARD_FILES.items():
            file_path = self.bank_path / filename
            if not file_path.exists():
                file_path.write_text(content, encoding="utf-8")
    
    def _text_to_embedding(self, text: str) -> Optional[bytes]:
        """Convert text to embedding vector bytes"""
        if not self.embedder:
            return None
        try:
            embedding = list(self.embedder.embed([text]))[0]
            return embedding.astype(np.float32).tobytes()
        except Exception as e:
            print(f"[Mnemo] Embedding error: {e}")
            return None
    
    def _embedding_to_text(self, blob: bytes) -> Optional[Any]:
        """Convert blob back to numpy array"""
        if not np or not blob:
            return None
        try:
            return np.frombuffer(blob, dtype=np.float32)
        except Exception:
            return None
    
    def add(self, content: str, tier: str = "learned", 
            metadata: Dict = None, importance: float = None,
            ttl_days: int = None) -> str:
        """
        Add a memory with optional TTL
        
        Args:
            content: Memory content
            tier: core/learned/episodic/working/procedural
            metadata: Additional key-value pairs
            importance: 0.0-1.0 (auto-calculated if None)
            ttl_days: Auto-expire after N days (for working tier)
        
        Returns:
            Memory ID
        """
        memory_id = str(uuid.uuid4())
        
        # Auto-calculate importance if not provided
        if importance is None:
            importance = self._calculate_importance(content, tier, metadata)
        
        # Calculate expiry
        expires_at = None
        if ttl_days or tier == "working":
            days = ttl_days or 7
            expires_at = (datetime.now() + timedelta(days=days)).isoformat()
        
        # Generate embedding
        embedding_blob = self._text_to_embedding(content)
        
        # Store metadata
        meta = metadata or {}
        meta['tier'] = tier
        meta['created'] = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO memories (id, tier, content, metadata, importance, expires_at, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (memory_id, tier, content, json.dumps(meta), importance, expires_at, embedding_blob))
        
        return memory_id
    
    def _calculate_importance(self, content: str, tier: str, metadata: Dict) -> float:
        """Calculate importance score (0.0-1.0)"""
        score = 0.0
        
        # Tier base score
        tier_scores = {
            "core": 1.0,
            "procedural": 0.8,
            "learned": 0.5,
            "episodic": 0.3,
            "working": 0.1
        }
        score += tier_scores.get(tier, 0.5)
        
        # Length bonus (structured content is more important)
        if len(content) > 100:
            score += 0.1
        
        # Specificity bonus (contains specific identifiers)
        import re
        if re.search(r'\b[A-Za-z_][A-Za-z0-9_]*\b', content):  # Contains identifiers
            score += 0.1
        
        return min(score, 1.0)
    
    def search_hybrid(self, query: str, limit: int = 5, 
                     tier_filter: List[str] = None,
                     weights: Dict[str, float] = None) -> List[Dict]:
        """
        Hybrid search: BM25 (FTS5) + Vector similarity + RRF fusion
        
        Args:
            query: Search query
            limit: Max results
            tier_filter: Only search these tiers
            weights: {'bm25': 0.4, 'vector': 0.6}
        
        Returns:
            List of memories with scores
        """
        if weights is None:
            weights = {'bm25': 0.4, 'vector': 0.6}
        
        # Prune expired memories first
        self._prune_expired()
        
        # Get BM25 results
        bm25_results = self._search_bm25(query, limit * 2)
        
        # Get vector results
        vector_results = self._search_vector(query, limit * 2)
        
        # RRF fusion
        fused = self._rrf_fusion(bm25_results, vector_results, weights)
        
        # Apply tier filter
        if tier_filter:
            fused = [m for m in fused if m['tier'] in tier_filter]
        
        # Update access count
        for memory in fused[:limit]:
            self._increment_access(memory['id'])
        
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
                
                # Build FTS5 query: word1 OR word2 OR ...
                fts_query = " OR ".join(words)
                
                # Simple MATCH query (FTS5 returns results in relevance order by default)
                rows = conn.execute("""
                    SELECT m.id, m.tier, m.content, m.metadata, m.importance, m.access_count
                    FROM memories m
                    JOIN memories_fts ON m.rowid = memories_fts.rowid
                    WHERE memories_fts MATCH ?
                    LIMIT ?
                """, (fts_query, limit)).fetchall()
                
                for i, row in enumerate(rows):
                    results.append({
                        'id': row['id'],
                        'tier': row['tier'],
                        'content': row['content'],
                        'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                        'importance': row['importance'],
                        'access_count': row['access_count'],
                        'score': len(rows) - i,  # Approximate rank score
                        'source': 'bm25'
                    })
        except Exception as e:
            print(f"[Mnemo] BM25 search error: {e}")
        
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
                    SELECT id, tier, content, metadata, importance, access_count, embedding
                    FROM memories
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
                        'id': row['id'],
                        'tier': row['tier'],
                        'content': row['content'],
                        'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                        'importance': row['importance'],
                        'access_count': row['access_count'],
                        'score': float(similarity),
                        'source': 'vector'
                    })
                
                # Sort by similarity
                results.sort(key=lambda x: x['score'], reverse=True)
                results = results[:limit]
                
        except Exception as e:
            print(f"[Mnemo] Vector search error: {e}")
        
        return results
    
    def _rrf_fusion(self, bm25_results: List[Dict], vector_results: List[Dict], 
                     weights: Dict[str, float], k: int = 60) -> List[Dict]:
        """
        Reciprocal Rank Fusion (RRF) with weights
        
        Formula: score = w_bm25/(k + rank_bm25) + w_vector/(k + rank_vector)
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
                score += weights['bm25'] / (k + bm25_rank)
            if vector_rank:
                score += weights['vector'] / (k + vector_rank)
            
            # Use the richer data source
            data = vector_data if vector_data else bm25_data
            if data:
                data['score'] = score
                data['rrf_score'] = score
                data['bm25_rank'] = bm25_rank
                data['vector_rank'] = vector_rank
                fused.append(data)
        
        # Sort by RRF score
        fused.sort(key=lambda x: x['score'], reverse=True)
        
        return fused
    
    def _increment_access(self, memory_id: str):
        """Increment access count"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE memories 
                    SET access_count = access_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (memory_id,))
        except Exception:
            pass
    
    def _prune_expired(self):
        """Remove expired working memories"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    DELETE FROM memories 
                    WHERE expires_at IS NOT NULL AND expires_at < datetime('now')
                """)
        except Exception:
            pass
    
    def get_by_tier(self, tier: str, limit: int = 50) -> List[Dict]:
        """Get memories by tier"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT id, tier, content, metadata, importance, access_count, created_at
                FROM memories
                WHERE tier = ?
                ORDER BY importance DESC, access_count DESC
                LIMIT ?
            """, (tier, limit)).fetchall()
            
            return [dict(row) for row in rows]
    
    def consolidate(self, threshold: float = 0.9) -> int:
        """
        Find and merge near-duplicate memories
        Returns count of merged memories
        """
        if not self.embedder:
            return 0
        
        merged = 0
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute("""
                    SELECT id, content, embedding, tier
                    FROM memories
                    WHERE embedding IS NOT NULL
                """).fetchall()
                
                embeddings = {}
                for row in rows:
                    if row['embedding']:
                        embeddings[row['id']] = np.frombuffer(row['embedding'], dtype=np.float32)
                
                # Find pairs with high similarity
                to_merge = []
                processed = set()
                
                for id1, emb1 in embeddings.items():
                    if id1 in processed:
                        continue
                    for id2, emb2 in embeddings.items():
                        if id2 in processed or id1 == id2:
                            continue
                        
                        # Cosine similarity
                        dot = np.dot(emb1, emb2)
                        norm1 = np.linalg.norm(emb1)
                        norm2 = np.linalg.norm(emb2)
                        
                        if norm1 == 0 or norm2 == 0:
                            continue
                        
                        sim = dot / (norm1 * norm2)
                        
                        if sim >= threshold:
                            to_merge.append((id1, id2))
                            processed.add(id2)
                    processed.add(id1)
                
                # Merge (keep first, delete second, update metadata)
                for keep_id, delete_id in to_merge:
                    conn.execute("DELETE FROM memories WHERE id = ?", (delete_id,))
                    merged += 1
                
        except Exception as e:
            print(f"[Mnemo] Consolidation error: {e}")
        
        return merged
    
    def read(self, filename: str) -> str:
        """Backward compatible: read markdown file"""
        file_path = self.bank_path / filename
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return ""
    
    def write(self, filename: str, content: str):
        """Backward compatible: write markdown file"""
        file_path = self.bank_path / filename
        file_path.write_text(content, encoding="utf-8")
    
    def get_snapshot(self, tier_filter: List[str] = None) -> Dict:
        """Get a summary of memories for context injection"""
        snapshot = {}
        
        # Legacy files
        for filename in self.STANDARD_FILES.keys():
            content = self.read(filename)
            snapshot[filename] = content[:2000] + "..." if len(content) > 2000 else content
        
        # New: database memories by tier
        tiers = tier_filter or ['core', 'procedural', 'learned']
        for tier in tiers:
            memories = self.get_by_tier(tier, limit=10)
            if memories:
                snapshot[f"memories_{tier}"] = [
                    {
                        'content': m['content'][:500],
                        'importance': m['importance']
                    }
                    for m in memories[:5]
                ]
        
        return snapshot
