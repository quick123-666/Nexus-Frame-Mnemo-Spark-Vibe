#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV Data Models for Frame (Graph-Document Rule Engine)
"""
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class RuleNode:
    """Represents a single rule in the Frame graph."""
    id: str
    category: str
    content: str
    weight: int = 10
    triggers: List[str] = field(default_factory=list)
    lifecycle: str = "active"

@dataclass
class RuleEdge:
    """Represents a relationship between two rules."""
    source_id: str
    target_id: str
    relation_type: str # inherits, requires, overrides, conflicts
