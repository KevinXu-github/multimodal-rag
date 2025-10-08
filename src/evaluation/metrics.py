"""Evaluation metrics for the multimodal RAG system."""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class QueryType(Enum):
    """Types of queries the system supports."""
    FACTUAL = "factual"
    LOOKUP = "lookup"
    SUMMARIZATION = "summarization"
    SEMANTIC_LINKAGE = "semantic_linkage"
    REASONING = "reasoning"


class MetricType(Enum):
    """Metrics tracked for evaluation."""
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    HALLUCINATION_RATE = "hallucination_rate"
    LATENCY = "latency"
    RETRIEVAL_PRECISION = "retrieval_precision"
    RETRIEVAL_RECALL = "retrieval_recall"
    CONTEXT_RELEVANCE = "context_relevance"
    ANSWER_FAITHFULNESS = "answer_faithfulness"


@dataclass
class EvaluationCriteria:
    """Defines what constitutes a correct response for each query type."""
    query_type: QueryType
    min_accuracy: float = 0.8
    min_relevance: float = 0.75
    max_hallucination_rate: float = 0.1
    max_latency_ms: float = 5000
    min_retrieval_precision: float = 0.7
    min_context_relevance: float = 0.8
    min_answer_faithfulness: float = 0.85


DEFAULT_CRITERIA: Dict[QueryType, EvaluationCriteria] = {
    QueryType.FACTUAL: EvaluationCriteria(
        query_type=QueryType.FACTUAL,
        min_accuracy=0.9,
        min_relevance=0.85,
        max_hallucination_rate=0.05,
        max_latency_ms=3000,
    ),
    QueryType.LOOKUP: EvaluationCriteria(
        query_type=QueryType.LOOKUP,
        min_accuracy=0.85,
        min_relevance=0.8,
        max_hallucination_rate=0.1,
        max_latency_ms=2000,
    ),
    QueryType.SUMMARIZATION: EvaluationCriteria(
        query_type=QueryType.SUMMARIZATION,
        min_accuracy=0.75,
        min_relevance=0.7,
        max_hallucination_rate=0.15,
        max_latency_ms=8000,
    ),
    QueryType.SEMANTIC_LINKAGE: EvaluationCriteria(
        query_type=QueryType.SEMANTIC_LINKAGE,
        min_accuracy=0.8,
        min_relevance=0.75,
        max_hallucination_rate=0.1,
        max_latency_ms=6000,
    ),
    QueryType.REASONING: EvaluationCriteria(
        query_type=QueryType.REASONING,
        min_accuracy=0.75,
        min_relevance=0.7,
        max_hallucination_rate=0.15,
        max_latency_ms=10000,
    ),
}


@dataclass
class EvaluationResult:
    """Result of evaluating a single query."""
    query: str
    query_type: QueryType
    expected_answer: Optional[str]
    actual_answer: str
    retrieved_contexts: List[str]
    metrics: Dict[MetricType, float]
    passed: bool
    failure_reasons: List[str]
    latency_ms: float


class GracefulFailureHandler:
    """Handles graceful failure scenarios."""

    @staticmethod
    def no_context_found() -> str:
        return (
            "I couldn't find relevant information to answer your question. "
            "This might be outside my current knowledge base. "
            "Please try rephrasing or asking about a different topic."
        )

    @staticmethod
    def out_of_domain() -> str:
        return (
            "This question appears to be outside my domain expertise. "
            "I can only answer questions based on the ingested documents."
        )

    @staticmethod
    def processing_error(modality: str) -> str:
        return (
            f"I encountered an error processing {modality} content. "
            f"Please ensure the file format is supported and try again."
        )

    @staticmethod
    def service_unavailable(service: str) -> str:
        return (
            f"The {service} service is temporarily unavailable. "
            f"Please try again in a moment."
        )

    @staticmethod
    def validation_error(reason: str) -> str:
        return (
            f"Input validation failed: {reason}. "
            f"Please check your input and try again."
        )
