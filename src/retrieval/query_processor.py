"""Query processing and validation."""

from typing import Optional, Tuple, List
from dataclasses import dataclass
from ..evaluation.metrics import QueryType
from .query_expander import QueryExpander, MultiQueryGenerator


@dataclass
class ProcessedQuery:
    """Processed and validated query."""
    original_query: str
    processed_query: str
    query_type: QueryType
    is_valid: bool
    validation_error: Optional[str] = None
    expanded_queries: Optional[List[str]] = None
    rewritten_query: Optional[str] = None


class QueryProcessor:
    """Processes and validates user queries."""

    MIN_QUERY_LENGTH = 3
    MAX_QUERY_LENGTH = 500

    def __init__(self, enable_expansion: bool = True, enable_rewriting: bool = True):
        """
        Initialize query processor.

        Args:
            enable_expansion: Enable query expansion
            enable_rewriting: Enable query rewriting
        """
        self.enable_expansion = enable_expansion
        self.enable_rewriting = enable_rewriting
        self.expander = QueryExpander()
        self.multi_query_gen = MultiQueryGenerator(self.expander)

    def process(self, query: str) -> ProcessedQuery:
        """Process and validate query."""
        is_valid, error = self.validate(query)

        if not is_valid:
            return ProcessedQuery(
                original_query=query,
                processed_query="",
                query_type=QueryType.FACTUAL,
                is_valid=False,
                validation_error=error,
                expanded_queries=None,
                rewritten_query=None,
            )

        # Clean and normalize
        processed = self._clean_query(query)

        # Classify query type
        query_type = self._classify_query(processed)

        # Expand query (if enabled)
        expanded_queries = None
        if self.enable_expansion:
            expanded_queries = self.expander.expand(processed)

        # Rewrite query (if enabled)
        rewritten_query = None
        if self.enable_rewriting:
            rewritten_query = self.expander.rewrite(processed, query_type.value)

        # Use rewritten query if available, otherwise use processed
        final_query = rewritten_query if rewritten_query else processed

        return ProcessedQuery(
            original_query=query,
            processed_query=final_query,
            query_type=query_type,
            is_valid=True,
            expanded_queries=expanded_queries,
            rewritten_query=rewritten_query,
        )

    def validate(self, query: str) -> Tuple[bool, Optional[str]]:
        """Validate query."""
        if not query or not query.strip():
            return False, "Query is empty"

        if len(query) < self.MIN_QUERY_LENGTH:
            return False, f"Query too short (min {self.MIN_QUERY_LENGTH} chars)"

        if len(query) > self.MAX_QUERY_LENGTH:
            return False, f"Query too long (max {self.MAX_QUERY_LENGTH} chars)"

        return True, None

    def _clean_query(self, query: str) -> str:
        """Clean and normalize query."""
        cleaned = query.strip()
        cleaned = " ".join(cleaned.split())
        return cleaned

    def _classify_query(self, query: str) -> QueryType:
        """Classify query type."""
        query_lower = query.lower()

        if any(word in query_lower for word in ["who", "what", "when", "where"]):
            return QueryType.FACTUAL

        if any(word in query_lower for word in ["find", "list", "show", "get"]):
            return QueryType.LOOKUP

        if any(word in query_lower for word in ["summarize", "summary", "overview"]):
            return QueryType.SUMMARIZATION

        if any(word in query_lower for word in ["connect", "link", "relate", "between"]):
            return QueryType.SEMANTIC_LINKAGE

        if any(word in query_lower for word in ["why", "how", "explain", "analyze"]):
            return QueryType.REASONING

        return QueryType.FACTUAL
