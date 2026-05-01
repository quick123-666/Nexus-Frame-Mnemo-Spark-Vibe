#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV Frame Engine: Graph-Document Rule Reasoner
"""
import sqlite3
import json
import os
from typing import List, Dict, Set, Optional
from .models import RuleNode, RuleEdge

class FrameEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rules (
                    id TEXT PRIMARY KEY,
                    category TEXT,
                    content TEXT,
                    weight INTEGER DEFAULT 10,
                    triggers TEXT, -- JSON array
                    lifecycle TEXT DEFAULT 'active'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    source_id TEXT,
                    target_id TEXT,
                    relation_type TEXT,
                    PRIMARY KEY (source_id, target_id, relation_type)
                )
            """)

    def add_rule(self, rule: RuleNode):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO rules VALUES (?, ?, ?, ?, ?, ?)",
                         (rule.id, rule.category, rule.content, rule.weight, json.dumps(rule.triggers), rule.lifecycle))

    def add_edge(self, edge: RuleEdge):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO edges VALUES (?, ?, ?)",
                         (edge.source_id, edge.target_id, edge.relation_type))

    def resolve_rules(self, context_tags: List[str]) -> List[RuleNode]:
        """
        Core Logic: Resolve rules based on context tags and graph relations.
        1. Find directly matching rules.
        2. Expand via 'requires' relations.
        3. Remove 'conflicts' if higher weight exists or explicit override.
        """
        matched_ids: Set[str] = set()
        all_rules: Dict[str, RuleNode] = {}

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # 1. Direct Match
            for tag in context_tags:
                for row in conn.execute("SELECT * FROM rules WHERE triggers LIKE ?", (f'%"{tag}"%',)):
                    rule = self._row_to_rule(row)
                    if rule.id not in matched_ids:
                        matched_ids.add(rule.id)
                        all_rules[rule.id] = rule

            # 2. Expansion (requires) & Conflict Detection
            # Simplified for Phase 1: Just fetch connected rules and check conflicts
            conflicts_to_remove = set()
            requires_to_add = set()

            for rule_id in list(matched_ids):
                # Check for requires
                for row in conn.execute("SELECT target_id FROM edges WHERE source_id = ? AND relation_type = 'requires'", (rule_id,)):
                    requires_to_add.add(row[0])
                
                # Check for conflicts
                for row in conn.execute("SELECT target_id FROM edges WHERE source_id = ? AND relation_type = 'conflicts'", (rule_id,)):
                    target_id = row[0]
                    target_rule = self._get_rule(conn, target_id)
                    if target_rule and target_rule.weight < all_rules[rule_id].weight:
                        conflicts_to_remove.add(target_id)
                    # Note: Real conflict resolution is more complex, this is Phase 1 heuristic

            # Add required rules
            for req_id in requires_to_add:
                if req_id not in matched_ids:
                    req_rule = self._get_rule(conn, req_id)
                    if req_rule:
                        matched_ids.add(req_id)
                        all_rules[req_id] = req_rule

            # Remove conflicted rules
            for conf_id in conflicts_to_remove:
                if conf_id in matched_ids:
                    matched_ids.remove(conf_id)
                    if conf_id in all_rules:
                        del all_rules[conf_id]

        # Sort by weight (highest priority first)
        return sorted(all_rules.values(), key=lambda r: r.weight, reverse=True)

    def _row_to_rule(self, row) -> RuleNode:
        return RuleNode(
            id=row['id'],
            category=row['category'],
            content=row['content'],
            weight=row['weight'],
            triggers=json.loads(row['triggers']),
            lifecycle=row['lifecycle']
        )

    def _get_rule(self, conn, rule_id: str) -> Optional[RuleNode]:
        row = conn.execute("SELECT * FROM rules WHERE id = ?", (rule_id,)).fetchone()
        return self._row_to_rule(row) if row else None
