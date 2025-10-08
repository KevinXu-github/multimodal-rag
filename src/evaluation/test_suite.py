"""Minimal test suite for the RAG system."""

from typing import List
from .evaluator import TestCase
from .metrics import QueryType


def get_minimal_test_suite() -> List[TestCase]:
    """Returns minimal test suite for evaluation."""
    return [
        TestCase(
            query="What is the main topic of this document?",
            query_type=QueryType.FACTUAL,
            expected_answer=None,
        ),
        TestCase(
            query="Find all mentions of John Smith",
            query_type=QueryType.LOOKUP,
            expected_answer=None,
        ),
        TestCase(
            query="Summarize the key findings",
            query_type=QueryType.SUMMARIZATION,
            expected_answer=None,
        ),
        TestCase(
            query="What connections exist between the image and the text?",
            query_type=QueryType.SEMANTIC_LINKAGE,
            expected_answer=None,
        ),
        TestCase(
            query="Based on the evidence, what can we conclude?",
            query_type=QueryType.REASONING,
            expected_answer=None,
        ),
    ]


def get_factual_test_cases() -> List[TestCase]:
    """Test cases for factual queries."""
    return [
        TestCase(
            query="What is the date mentioned in the document?",
            query_type=QueryType.FACTUAL,
        ),
        TestCase(
            query="Who is the author?",
            query_type=QueryType.FACTUAL,
        ),
    ]


def get_lookup_test_cases() -> List[TestCase]:
    """Test cases for entity lookup."""
    return [
        TestCase(
            query="Find all people mentioned",
            query_type=QueryType.LOOKUP,
        ),
        TestCase(
            query="List all organizations referenced",
            query_type=QueryType.LOOKUP,
        ),
    ]


def get_cross_modal_test_cases() -> List[TestCase]:
    """Test cases for cross-modal queries."""
    return [
        TestCase(
            query="What person appears in both the image and transcript?",
            query_type=QueryType.SEMANTIC_LINKAGE,
        ),
        TestCase(
            query="Connect the audio content to the written document",
            query_type=QueryType.SEMANTIC_LINKAGE,
        ),
    ]
