"""Hybrid search combining graph, keyword, and vector retrieval."""

import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..storage.graph_store import Neo4jGraphStore
from ..storage.vector_store import QdrantVectorStore

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Single search result."""
    content: str
    score: float
    source: str
    metadata: Dict[str, Any]
    retrieval_method: str


@dataclass
class HybridSearchResult:
    """Result from hybrid search."""
    results: List[SearchResult]
    total_results: int
    graph_results: int
    vector_results: int
    keyword_results: int
    retrieval_time_ms: float


class HybridSearchEngine:
    """Hybrid search combining multiple retrieval strategies."""

    def __init__(
        self,
        graph_store: Neo4jGraphStore,
        vector_store: QdrantVectorStore,
        graph_weight: float = 0.3,
        vector_weight: float = 0.5,
        keyword_weight: float = 0.2,
    ):
        """Initialize hybrid search engine."""
        self.graph_store = graph_store
        self.vector_store = vector_store
        self.graph_weight = graph_weight
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight

    def search(
        self,
        query: str,
        top_k: int = 10,
        use_graph: bool = True,
        use_vector: bool = True,
        use_keyword: bool = True,
        filters: Optional[Dict[str, Any]] = None,
    ) -> HybridSearchResult:
        """Perform hybrid search."""
        start_time = time.time()

        all_results = []
        graph_count = 0
        vector_count = 0
        keyword_count = 0

        if use_vector:
            vector_results = self._vector_search(query, top_k, filters)
            all_results.extend(vector_results)
            vector_count = len(vector_results)

        if use_graph:
            graph_results = self._graph_search(query, top_k)
            all_results.extend(graph_results)
            graph_count = len(graph_results)

        if use_keyword:
            keyword_results = self._keyword_search(query, top_k, filters)
            all_results.extend(keyword_results)
            keyword_count = len(keyword_results)

        merged_results = self._merge_and_rerank(all_results, top_k)

        retrieval_time_ms = (time.time() - start_time) * 1000

        return HybridSearchResult(
            results=merged_results,
            total_results=len(merged_results),
            graph_results=graph_count,
            vector_results=vector_count,
            keyword_results=keyword_count,
            retrieval_time_ms=retrieval_time_ms,
        )

    def _vector_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Semantic vector search."""
        results = []

        try:
            vector_results = self.vector_store.search(
                query=query,
                top_k=top_k,
                filters=filters,
            )

            for result in vector_results:
                results.append(
                    SearchResult(
                        content=result["text"],
                        score=result["score"] * self.vector_weight,
                        source=result["metadata"].get("source_file", "unknown"),
                        metadata=result["metadata"],
                        retrieval_method="vector",
                    )
                )

        except Exception as e:
            logger.error(f"Vector search error: {e}", exc_info=True)

        return results

    def _graph_search(
        self,
        query: str,
        top_k: int,
    ) -> List[SearchResult]:
        """Graph traversal search."""
        results = []

        try:
            entities = self._extract_entities_from_query(query)

            for entity_name in entities[:3]:
                related_entities = self.graph_store.find_related_entities(
                    entity_name=entity_name,
                    max_hops=2,
                )

                for entity in related_entities[:top_k]:
                    results.append(
                        SearchResult(
                            content=f"Entity: {entity.get('name', '')} (Type: {entity.get('type', '')})",
                            score=entity.get('confidence', 0.7) * self.graph_weight,
                            source=entity.get('source_file', 'unknown'),
                            metadata=entity,
                            retrieval_method="graph",
                        )
                    )

        except Exception as e:
            logger.error(f"Graph search error: {e}", exc_info=True)

        return results

    def _keyword_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Keyword-based filtering search."""
        results = []

        try:
            keywords = self._extract_keywords(query)

            vector_results = self.vector_store.search(
                query=" ".join(keywords),
                top_k=top_k,
                filters=filters,
            )

            for result in vector_results:
                keyword_match_score = self._calculate_keyword_match(
                    keywords,
                    result["text"],
                )

                results.append(
                    SearchResult(
                        content=result["text"],
                        score=keyword_match_score * self.keyword_weight,
                        source=result["metadata"].get("source_file", "unknown"),
                        metadata=result["metadata"],
                        retrieval_method="keyword",
                    )
                )

        except Exception as e:
            logger.error(f"Keyword search error: {e}", exc_info=True)

        return results

    def _merge_and_rerank(
        self,
        results: List[SearchResult],
        top_k: int,
    ) -> List[SearchResult]:
        """Merge and rerank results from different sources."""
        content_map: Dict[str, SearchResult] = {}

        for result in results:
            key = result.content[:100]

            if key in content_map:
                content_map[key].score += result.score
            else:
                content_map[key] = result

        merged = list(content_map.values())
        merged.sort(key=lambda x: x.score, reverse=True)

        return merged[:top_k]

    def _extract_entities_from_query(self, query: str) -> List[str]:
        """Extract potential entity names from query."""
        words = query.split()
        capitalized = [w for w in words if w[0].isupper() and len(w) > 2]
        return capitalized if capitalized else words[:3]

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query."""
        stopwords = {"the", "a", "an", "in", "on", "at", "to", "for", "of", "with"}
        words = query.lower().split()
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        return keywords

    def _calculate_keyword_match(self, keywords: List[str], text: str) -> float:
        """Calculate keyword match score."""
        text_lower = text.lower()
        matches = sum(1 for kw in keywords if kw in text_lower)
        return matches / len(keywords) if keywords else 0.0
