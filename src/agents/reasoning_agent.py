"""Reasoning agent - focuses on multi-hop retrieval for complex queries."""

from .base_agent import BaseAgent, AgentResult


class ReasoningAgent(BaseAgent):
    """Agent specialized for reasoning queries requiring multi-hop inference."""

    def retrieve(self, query: str, top_k: int = 5) -> AgentResult:
        """Retrieve using multi-hop graph traversal strategy."""
        contexts = []
        metadata = {"strategy": "multi_hop_reasoning"}

        # Use deeper graph traversal for reasoning
        if self.graph_store:
            entities = self._extract_entities(query)

            for entity in entities[:2]:
                try:
                    # Deeper traversal (2 hops) for reasoning
                    related = self.graph_store.find_related_entities(
                        entity_name=entity,
                        max_hops=2
                    )
                    for rel_entity in related[:3]:
                        context = f"Entity: {rel_entity.get('name')} (Type: {rel_entity.get('type')})"
                        if rel_entity.get('context'):
                            context += f"\n{rel_entity.get('context')}"
                        contexts.append(context)
                except:
                    pass

        # Add vector results for broader context
        if self.vector_store:
            vector_results = self.vector_store.search(query, top_k=top_k)
            contexts.extend([r["text"] for r in vector_results])

        return AgentResult(
            contexts=contexts[:top_k * 2],  # More context for reasoning
            metadata=metadata,
            confidence=0.70 if contexts else 0.3,
            agent_name="ReasoningAgent"
        )

    def get_strategy(self) -> str:
        return "Multi-hop graph traversal with vector augmentation"

    def _extract_entities(self, query: str):
        """Extract entities from query."""
        words = query.split()
        entities = [w.strip(".,!?") for w in words if w and w[0].isupper() and len(w) > 2]
        return entities if entities else words[:3]
