"""Lookup agent - focuses on broad keyword-based retrieval."""

from .base_agent import BaseAgent, AgentResult


class LookupAgent(BaseAgent):
    """Agent specialized for lookup queries requiring comprehensive results."""

    def retrieve(self, query: str, top_k: int = 5) -> AgentResult:
        """Retrieve using keyword-focused strategy."""
        contexts = []
        metadata = {"strategy": "keyword_focused"}

        # Extract keywords
        keywords = self._extract_keywords(query)

        # Use vector search with keyword filtering
        if self.vector_store:
            # Expand top_k to get more candidates for filtering
            vector_results = self.vector_store.search(query, top_k=top_k * 2)

            # Filter by keyword presence
            for result in vector_results:
                text = result["text"].lower()
                keyword_matches = sum(1 for kw in keywords if kw in text)
                if keyword_matches > 0:
                    contexts.append(result["text"])
                    if len(contexts) >= top_k:
                        break

        return AgentResult(
            contexts=contexts[:top_k],
            metadata=metadata,
            confidence=0.75 if contexts else 0.3,
            agent_name="LookupAgent"
        )

    def get_strategy(self) -> str:
        return "Keyword-focused vector retrieval with filtering"

    def _extract_keywords(self, query: str):
        """Extract keywords from query."""
        stopwords = {"the", "a", "an", "in", "on", "at", "to", "for", "of", "with",
                     "is", "are", "was", "were", "be", "been", "what", "where",
                     "when", "who", "how", "find", "list", "show", "get"}
        words = query.lower().split()
        return [w.strip(".,!?") for w in words if w not in stopwords and len(w) > 2]
