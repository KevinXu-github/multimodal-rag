"""Factual query agent - focuses on precise entity-based retrieval."""

from typing import List
from .base_agent import BaseAgent, AgentResult


class FactualAgent(BaseAgent):
    """Agent specialized for factual queries requiring precise answers."""

    def retrieve(self, query: str, top_k: int = 5) -> AgentResult:
        """Retrieve using entity-focused strategy."""
        contexts = []
        metadata = {"strategy": "entity_focused"}

        # Prioritize graph retrieval for factual queries
        if self.graph_store:
            # Extract potential entities from query
            entities = self._extract_entities(query)

            for entity in entities[:3]:
                try:
                    related = self.graph_store.find_related_entities(
                        entity_name=entity,
                        max_hops=1
                    )
                    for rel_entity in related[:2]:
                        context = f"Entity: {rel_entity.get('name')} (Type: {rel_entity.get('type')})"
                        if rel_entity.get('context'):
                            context += f"\nContext: {rel_entity.get('context')}"
                        contexts.append(context)
                except:
                    pass

        # Supplement with vector search
        if self.vector_store and len(contexts) < top_k:
            vector_results = self.vector_store.search(query, top_k=top_k - len(contexts))
            contexts.extend([r["text"] for r in vector_results])

        return AgentResult(
            contexts=contexts[:top_k],
            metadata=metadata,
            confidence=0.85 if contexts else 0.3,
            agent_name="FactualAgent"
        )

    def get_strategy(self) -> str:
        return "Entity-focused retrieval with graph traversal"

    def _extract_entities(self, query: str) -> List[str]:
        """Extract potential entity names from query."""
        words = query.split()
        # Simple heuristic: capitalized words are likely entities
        entities = [w.strip(".,!?") for w in words if w and w[0].isupper() and len(w) > 2]
        return entities if entities else words[:3]
