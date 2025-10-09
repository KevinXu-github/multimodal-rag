"""Agent router for query-type-based retrieval orchestration."""

from typing import Optional
from ..evaluation.metrics import QueryType
from .base_agent import BaseAgent, AgentResult
from .factual_agent import FactualAgent
from .lookup_agent import LookupAgent
from .reasoning_agent import ReasoningAgent


class AgentRouter:
    """Routes queries to appropriate specialized agents."""

    def __init__(self, graph_store=None, vector_store=None):
        """Initialize router with storage backends."""
        self.graph_store = graph_store
        self.vector_store = vector_store

        # Initialize all agents
        self.agents = {
            QueryType.FACTUAL: FactualAgent(graph_store, vector_store),
            QueryType.LOOKUP: LookupAgent(graph_store, vector_store),
            QueryType.SUMMARIZATION: LookupAgent(graph_store, vector_store),  # Use lookup for summarization
            QueryType.SEMANTIC_LINKAGE: ReasoningAgent(graph_store, vector_store),
            QueryType.REASONING: ReasoningAgent(graph_store, vector_store),
        }

    def route(
        self,
        query: str,
        query_type: QueryType,
        top_k: int = 5
    ) -> AgentResult:
        """Route query to appropriate agent based on query type."""
        agent = self.agents.get(query_type)

        if not agent:
            # Fallback to factual agent
            agent = self.agents[QueryType.FACTUAL]

        return agent.retrieve(query, top_k=top_k)

    def get_agent(self, query_type: QueryType) -> Optional[BaseAgent]:
        """Get the agent for a specific query type."""
        return self.agents.get(query_type)
