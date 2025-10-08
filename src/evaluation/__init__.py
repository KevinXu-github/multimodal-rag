"""Evaluation module for RAG system."""

from .metrics import (
    QueryType,
    MetricType,
    EvaluationCriteria,
    EvaluationResult,
    GracefulFailureHandler,
)
from .evaluator import RAGEvaluator, TestCase
from .test_suite import (
    get_minimal_test_suite,
    get_factual_test_cases,
    get_lookup_test_cases,
    get_cross_modal_test_cases,
)

__all__ = [
    "QueryType",
    "MetricType",
    "EvaluationCriteria",
    "EvaluationResult",
    "GracefulFailureHandler",
    "RAGEvaluator",
    "TestCase",
    "get_minimal_test_suite",
    "get_factual_test_cases",
    "get_lookup_test_cases",
    "get_cross_modal_test_cases",
]
