"""Base agent for retrieval orchestration."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class AgentResult:
    """Result from an agent's execution."""
    contexts: List[str]
    metadata: Dict[str, Any]
    confidence: float
    agent_name: str


class BaseAgent(ABC):
    """Base class for retrieval agents."""

    def __init__(self, graph_store=None, vector_store=None):
        """Initialize agent with storage backends."""
        self.graph_store = graph_store
        self.vector_store = vector_store

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> AgentResult:
        """Retrieve relevant contexts for the query."""
        pass

    @abstractmethod
    def get_strategy(self) -> str:
        """Get the retrieval strategy name."""
        pass
