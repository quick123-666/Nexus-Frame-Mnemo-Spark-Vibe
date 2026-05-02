#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV Knowledge: LLM Wiki Integration
Scans and indexes LLM wiki knowledge base for coding guidance
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import json
import time

@dataclass
class KnowledgeDoc:
    """Represents a single knowledge document"""
    title: str
    path: str
    content: str
    keywords: List[str]
    category: str
    word_count: int
    indexed_at: float

@dataclass 
class SearchResult:
    """Represents a search result"""
    doc: KnowledgeDoc
    score: float
    matched_keywords: List[str]
    excerpt: str

class KnowledgeBase:
    """
    LLM Wiki 知识库
    
    功能:
    1. 扫描 wiki 目录并建立索引
    2. 关键词搜索相关知识文档
    3. 为 AI 决策提供编程最佳实践
    """
    
    def __init__(self, wiki_path: str = None, index_file: str = None):
        self.wiki_path = Path(wiki_path) if wiki_path else None
        self.index_file = Path(index_file) if index_file else None
        self.documents: List[KnowledgeDoc] = []
        self.keyword_index: Dict[str, List[int]] = {}  # keyword -> doc indices
        
    def load(self) -> bool:
        """加载知识库 (从缓存或扫描)"""
        if self.index_file and self.index_file.exists():
            return self._load_from_cache()
        
        if self.wiki_path and self.wiki_path.exists():
            return self._scan_and_index()
        
        return False
    
    def _scan_and_index(self) -> bool:
        """扫描 wiki 目录并建立索引"""
        print(f"Scanning Knowledge Base: {self.wiki_path}")
        
        self.documents = []
        self.keyword_index = {}
        
        # 扫描所有 markdown 文件
        md_files = list(self.wiki_path.rglob("*.md"))
        
        for md_file in md_files:
            try:
                doc = self._parse_document(md_file)
                if doc:
                    self.documents.append(doc)
                    self._update_keyword_index(len(self.documents) - 1, doc)
            except Exception as e:
                print(f"  Skipped {md_file.name}: {e}")
        
        print(f"Indexing complete: {len(self.documents)} documents, {len(self.keyword_index)} keywords")
        
        # 保存缓存
        if self.index_file:
            self._save_to_cache()
        
        return True
    
    def _parse_document(self, file_path: Path) -> Optional[KnowledgeDoc]:
        """解析单个 markdown 文档"""
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            
            # 提取标题 (第一个 # 标题)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else file_path.stem
            
            # 提取分类 (从路径中)
            rel_path = file_path.relative_to(self.wiki_path)
            category = rel_path.parts[0] if len(rel_path.parts) > 1 else "root"
            
            # 提取关键词
            keywords = self._extract_keywords(content, title)
            
            # 计算字数
            word_count = len(content.split())
            
            return KnowledgeDoc(
                title=title,
                path=str(rel_path),
                content=content[:5000],  # 限制长度
                keywords=keywords,
                category=category,
                word_count=word_count,
                indexed_at=time.time()
            )
        except Exception as e:
            return None
    
    def _extract_keywords(self, content: str, title: str) -> List[str]:
        """从文档中提取关键词"""
        keywords = set()
        
        # 从标题提取
        keywords.update(title.lower().split())
        
        # 常见编程关键词
        coding_keywords = [
            "python", "javascript", "typescript", "react", "vue", "django", "flask",
            "git", "docker", "api", "rest", "graphql", "database", "sql",
            "test", "debug", "deploy", "ci/cd", "security", "performance",
            "ai", "llm", "agent", "prompt", "context", "memory",
            "vibe coding", "best practice", "architecture", "design pattern",
            "function", "class", "module", "package", "dependency",
            "error handling", "logging", "configuration", "environment",
        ]
        
        content_lower = content.lower()
        for kw in coding_keywords:
            if kw in content_lower:
                keywords.add(kw)
        
        return list(keywords)
    
    def _update_keyword_index(self, doc_index: int, doc: KnowledgeDoc):
        """更新关键词索引"""
        for kw in doc.keywords:
            if kw not in self.keyword_index:
                self.keyword_index[kw] = []
            self.keyword_index[kw].append(doc_index)
    
    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """搜索相关知识文档"""
        query_keywords = query.lower().split()
        results = []
        
        # 找到所有匹配的文档
        matched_docs = set()
        for kw in query_keywords:
            # 精确匹配
            if kw in self.keyword_index:
                matched_docs.update(self.keyword_index[kw])
            
            # 模糊匹配 (包含)
            for index_kw, indices in self.keyword_index.items():
                if kw in index_kw or index_kw in kw:
                    matched_docs.update(indices)
        
        # 计算相关性分数
        for doc_index in matched_docs:
            doc = self.documents[doc_index]
            score = 0
            matched_kws = []
            
            for kw in query_keywords:
                if kw in doc.keywords:
                    score += 3
                    matched_kws.append(kw)
                elif kw in doc.content.lower():
                    score += 1
                    matched_kws.append(kw)
            
            if score > 0:
                # 提取相关摘要
                excerpt = self._extract_excerpt(doc.content, query_keywords)
                
                results.append(SearchResult(
                    doc=doc,
                    score=score,
                    matched_keywords=list(set(matched_kws)),
                    excerpt=excerpt
                ))
        
        # 按分数排序
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:max_results]
    
    def _extract_excerpt(self, content: str, query_keywords: List[str], max_length: int = 200) -> str:
        """提取相关摘要"""
        content_lower = content.lower()
        
        # 找到第一个匹配关键词的位置
        best_pos = -1
        for kw in query_keywords:
            pos = content_lower.find(kw)
            if pos != -1 and (best_pos == -1 or pos < best_pos):
                best_pos = pos
        
        if best_pos == -1:
            return content[:max_length] + "..."
        
        # 提取上下文
        start = max(0, best_pos - 50)
        end = min(len(content), best_pos + max_length)
        
        excerpt = content[start:end].strip()
        if start > 0:
            excerpt = "..." + excerpt
        if end < len(content):
            excerpt = excerpt + "..."
        
        return excerpt
    
    def get_relevant_guidance(self, query: str, max_results: int = 3) -> str:
        """获取相关知识指导 (格式化文本)"""
        results = self.search(query, max_results)
        
        if not results:
            return "暂无相关知识文档。"
        
        guidance = "📚 相关知识指导:\n\n"
        for i, result in enumerate(results, 1):
            guidance += f"**{i}. {result.doc.title}** (相关度: {result.score})\n"
            guidance += f"   路径: {result.doc.path}\n"
            guidance += f"   匹配: {', '.join(result.matched_keywords)}\n"
            guidance += f"   摘要: {result.excerpt}\n\n"
        
        return guidance
    
    def _save_to_cache(self):
        """保存索引到缓存"""
        cache_data = {
            "wiki_path": str(self.wiki_path),
            "documents": [
                {
                    "title": doc.title,
                    "path": doc.path,
                    "content": doc.content,
                    "keywords": doc.keywords,
                    "category": doc.category,
                    "word_count": doc.word_count,
                    "indexed_at": doc.indexed_at,
                }
                for doc in self.documents
            ],
            "keyword_index": self.keyword_index,
        }
        
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    def _load_from_cache(self) -> bool:
        """从缓存加载索引"""
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            
            self.documents = [
                KnowledgeDoc(**doc_data)
                for doc_data in cache_data["documents"]
            ]
            self.keyword_index = cache_data["keyword_index"]
            
            print(f"Loaded from cache: {len(self.documents)} documents")
            return True
        except Exception as e:
            print(f"Cache load failed: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """获取知识库统计信息"""
        categories = {}
        for doc in self.documents:
            categories[doc.category] = categories.get(doc.category, 0) + 1
        
        return {
            "total_documents": len(self.documents),
            "total_keywords": len(self.keyword_index),
            "categories": categories,
            "wiki_path": str(self.wiki_path) if self.wiki_path else None,
        }
