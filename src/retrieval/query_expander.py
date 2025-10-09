"""Query expansion and rewriting for improved retrieval."""

from typing import List, Dict, Set
import re


class QueryExpander:
    """Expands and rewrites queries for better retrieval."""

    # Common synonyms for query expansion
    SYNONYMS = {
        "document": ["file", "paper", "text", "doc"],
        "find": ["locate", "search", "get", "retrieve"],
        "show": ["display", "list", "present"],
        "information": ["data", "details", "info"],
        "system": ["application", "platform", "software"],
        "create": ["build", "make", "generate", "construct"],
        "delete": ["remove", "erase", "drop"],
        "update": ["modify", "change", "edit", "alter"],
        "database": ["db", "datastore", "storage"],
        "error": ["issue", "problem", "bug", "failure"],
        "user": ["person", "individual", "account"],
        "requirement": ["specification", "spec", "need"],
        "feature": ["functionality", "capability", "function"],
        "test": ["check", "verify", "validate", "examine"],
        "code": ["program", "script", "implementation"],
    }

    def __init__(self):
        """Initialize query expander."""
        self.max_expansions = 3  # Limit number of expanded queries

    def expand(self, query: str) -> List[str]:
        """
        Expand query into multiple variations.

        Returns list of query variations including the original.
        """
        expansions = [query]  # Always include original

        # Add synonym-based expansion
        synonym_query = self._expand_with_synonyms(query)
        if synonym_query != query:
            expansions.append(synonym_query)

        # Add question reformulation
        reformulated = self._reformulate_question(query)
        if reformulated and reformulated != query:
            expansions.append(reformulated)

        # Add keyword extraction for broad search
        keyword_query = self._extract_keywords_query(query)
        if keyword_query and keyword_query != query:
            expansions.append(keyword_query)

        return expansions[:self.max_expansions]

    def rewrite(self, query: str, query_type: str = None) -> str:
        """
        Rewrite query for better retrieval based on query type.

        Args:
            query: Original query
            query_type: Type of query (factual, lookup, reasoning, etc.)

        Returns:
            Rewritten query optimized for the query type
        """
        # Clean and normalize
        query = self._normalize(query)

        # Type-specific rewriting
        if query_type == "factual":
            return self._rewrite_factual(query)
        elif query_type == "lookup":
            return self._rewrite_lookup(query)
        elif query_type == "summarization":
            return self._rewrite_summarization(query)
        elif query_type == "reasoning":
            return self._rewrite_reasoning(query)
        else:
            return query

    def _normalize(self, query: str) -> str:
        """Normalize query text."""
        # Remove extra whitespace
        query = " ".join(query.split())

        # Remove redundant question words at the end
        query = re.sub(r'\s+\?+$', '?', query)

        return query.strip()

    def _expand_with_synonyms(self, query: str) -> str:
        """Expand query by replacing words with synonyms."""
        words = query.lower().split()
        expanded_words = []

        for word in words:
            # Clean punctuation
            clean_word = word.strip(".,!?;:")

            # Check if word has synonyms
            if clean_word in self.SYNONYMS:
                # Add original word OR first synonym
                synonyms = self.SYNONYMS[clean_word]
                # Use first synonym for expansion
                expanded_words.append(synonyms[0] if synonyms else clean_word)
            else:
                expanded_words.append(word)

        return " ".join(expanded_words)

    def _reformulate_question(self, query: str) -> str:
        """Reformulate question into a different form."""
        query_lower = query.lower()

        # Convert "What is X?" to "X definition"
        what_is = re.match(r'what\s+(?:is|are)\s+(.+?)\??$', query_lower)
        if what_is:
            subject = what_is.group(1)
            return f"{subject} definition explanation"

        # Convert "How to X?" to "X procedure steps"
        how_to = re.match(r'how\s+(?:to|do\s+(?:i|you))\s+(.+?)\??$', query_lower)
        if how_to:
            action = how_to.group(1)
            return f"{action} procedure steps guide"

        # Convert "Where is X?" to "X location"
        where_is = re.match(r'where\s+(?:is|are)\s+(.+?)\??$', query_lower)
        if where_is:
            subject = where_is.group(1)
            return f"{subject} location position"

        # Convert "Why X?" to "X reason explanation"
        why = re.match(r'why\s+(.+?)\??$', query_lower)
        if why:
            subject = why.group(1)
            return f"{subject} reason explanation cause"

        return query

    def _extract_keywords_query(self, query: str) -> str:
        """Extract main keywords for broader search."""
        stopwords = {
            "the", "a", "an", "in", "on", "at", "to", "for", "of", "with",
            "is", "are", "was", "were", "be", "been", "being",
            "what", "where", "when", "who", "why", "how",
            "do", "does", "did", "can", "could", "would", "should",
            "this", "that", "these", "those",
            "i", "you", "we", "they", "it",
        }

        words = query.lower().split()
        keywords = [
            w.strip(".,!?;:")
            for w in words
            if w.strip(".,!?;:") not in stopwords and len(w) > 2
        ]

        return " ".join(keywords) if keywords else query

    def _rewrite_factual(self, query: str) -> str:
        """Rewrite factual queries to focus on entities and facts."""
        # Factual queries benefit from entity focus
        # Remove question words, keep entities
        query_lower = query.lower()

        # Remove common question starters
        query_lower = re.sub(r'^(what|who|when|where)\s+(is|are|was|were)\s+', '', query_lower)

        return query_lower.strip()

    def _rewrite_lookup(self, query: str) -> str:
        """Rewrite lookup queries to be more keyword-focused."""
        # Lookup queries benefit from keyword extraction
        return self._extract_keywords_query(query)

    def _rewrite_summarization(self, query: str) -> str:
        """Rewrite summarization queries to be broader."""
        query_lower = query.lower()

        # Remove "summarize" word and get the subject
        query_lower = re.sub(r'\b(summarize|summary|overview)\b', '', query_lower)
        query_lower = re.sub(r'\bthe\b', '', query_lower)

        return query_lower.strip()

    def _rewrite_reasoning(self, query: str) -> str:
        """Rewrite reasoning queries to focus on relationships."""
        # Reasoning queries benefit from keeping question structure
        # but expanding with relationship terms
        if "relationship" not in query.lower() and "connect" not in query.lower():
            query += " relationship connection"

        return query


class MultiQueryGenerator:
    """Generates multiple query variations for multi-query retrieval."""

    def __init__(self, expander: QueryExpander = None):
        """Initialize multi-query generator."""
        self.expander = expander or QueryExpander()

    def generate_multi_queries(self, query: str, num_queries: int = 3) -> List[str]:
        """
        Generate multiple variations of the query for multi-query retrieval.

        This is useful for improving recall by searching with different
        formulations of the same question.

        Args:
            query: Original query
            num_queries: Number of query variations to generate

        Returns:
            List of query variations
        """
        queries = [query]  # Always include original

        # Add expanded queries
        expanded = self.expander.expand(query)
        queries.extend([q for q in expanded if q not in queries])

        # Add decomposed sub-queries for complex questions
        if self._is_complex_query(query):
            sub_queries = self._decompose_query(query)
            queries.extend([q for q in sub_queries if q not in queries])

        return queries[:num_queries]

    def _is_complex_query(self, query: str) -> bool:
        """Check if query is complex (contains multiple questions)."""
        # Complex if has "and" or multiple question words
        question_words = ["what", "where", "when", "who", "why", "how"]
        query_lower = query.lower()

        question_count = sum(1 for word in question_words if word in query_lower)
        has_and = " and " in query_lower

        return question_count > 1 or has_and

    def _decompose_query(self, query: str) -> List[str]:
        """Decompose complex query into sub-queries."""
        sub_queries = []

        # Split on "and"
        if " and " in query.lower():
            parts = re.split(r'\s+and\s+', query, flags=re.IGNORECASE)
            sub_queries.extend([p.strip() for p in parts if p.strip()])

        # Split on commas for lists
        if "," in query:
            parts = query.split(",")
            sub_queries.extend([p.strip() for p in parts if len(p.strip()) > 10])

        return sub_queries
