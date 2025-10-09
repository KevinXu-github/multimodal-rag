"""Evaluation test cases for the RAG system."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.metrics import QueryType


class TestCase:
    """Test case for evaluation."""

    def __init__(self, query: str, query_type: QueryType, expected_keywords: list, description: str = ""):
        self.query = query
        self.query_type = query_type
        self.expected_keywords = expected_keywords  # Keywords that should appear in answer
        self.description = description


# Comprehensive test suite covering all 5 query types
EVALUATION_TEST_CASES = [
    # ==================== FACTUAL QUERIES ====================
    TestCase(
        query="What is a multimodal RAG system?",
        query_type=QueryType.FACTUAL,
        expected_keywords=["retrieval", "generation", "multimodal", "text", "image"],
        description="Basic factual question about RAG systems"
    ),
    TestCase(
        query="What is the purpose of a knowledge graph?",
        query_type=QueryType.FACTUAL,
        expected_keywords=["entities", "relationships", "structured", "data"],
        description="Factual question about knowledge graphs"
    ),
    TestCase(
        query="What is vector search?",
        query_type=QueryType.FACTUAL,
        expected_keywords=["semantic", "embeddings", "similarity", "search"],
        description="Factual question about vector search"
    ),

    # ==================== LOOKUP QUERIES ====================
    TestCase(
        query="Find all mentions of evaluation metrics",
        query_type=QueryType.LOOKUP,
        expected_keywords=["metrics", "evaluation", "accuracy", "relevance"],
        description="Lookup query for specific topic mentions"
    ),
    TestCase(
        query="List the supported file formats",
        query_type=QueryType.LOOKUP,
        expected_keywords=["pdf", "image", "audio", "format"],
        description="Lookup query for file formats"
    ),
    TestCase(
        query="Show me information about hybrid search",
        query_type=QueryType.LOOKUP,
        expected_keywords=["hybrid", "search", "graph", "vector", "keyword"],
        description="Lookup query for hybrid search"
    ),

    # ==================== SUMMARIZATION QUERIES ====================
    TestCase(
        query="Summarize the main requirements of the challenge",
        query_type=QueryType.SUMMARIZATION,
        expected_keywords=["multimodal", "knowledge graph", "hybrid search", "evaluation"],
        description="Summarization of challenge requirements"
    ),
    TestCase(
        query="Give me an overview of the system architecture",
        query_type=QueryType.SUMMARIZATION,
        expected_keywords=["pipeline", "ingestion", "retrieval", "generation"],
        description="Architecture overview summarization"
    ),
    TestCase(
        query="Summarize the evaluation framework",
        query_type=QueryType.SUMMARIZATION,
        expected_keywords=["query types", "metrics", "deepeval"],
        description="Evaluation framework summary"
    ),

    # ==================== SEMANTIC LINKAGE QUERIES ====================
    TestCase(
        query="How are entities connected across different modalities?",
        query_type=QueryType.SEMANTIC_LINKAGE,
        expected_keywords=["cross-modal", "linking", "entities", "relationship"],
        description="Cross-modal entity linking"
    ),
    TestCase(
        query="What is the relationship between the knowledge graph and vector database?",
        query_type=QueryType.SEMANTIC_LINKAGE,
        expected_keywords=["graph", "vector", "hybrid", "complementary"],
        description="Relationship between components"
    ),
    TestCase(
        query="How do query types relate to retrieval strategies?",
        query_type=QueryType.SEMANTIC_LINKAGE,
        expected_keywords=["query", "type", "retrieval", "strategy", "agent"],
        description="Query-to-strategy relationship"
    ),

    # ==================== REASONING QUERIES ====================
    TestCase(
        query="Why is hybrid search better than single-method retrieval?",
        query_type=QueryType.REASONING,
        expected_keywords=["hybrid", "multiple", "combined", "advantages", "recall", "precision"],
        description="Reasoning about hybrid search benefits"
    ),
    TestCase(
        query="How does the agent-based orchestration improve retrieval?",
        query_type=QueryType.REASONING,
        expected_keywords=["agent", "specialized", "query type", "optimization"],
        description="Reasoning about agent orchestration"
    ),
    TestCase(
        query="Explain why evaluation is important for RAG systems",
        query_type=QueryType.REASONING,
        expected_keywords=["evaluation", "quality", "metrics", "hallucination", "accuracy"],
        description="Reasoning about evaluation importance"
    ),
]


def get_test_cases_by_type(query_type: QueryType):
    """Get test cases filtered by query type."""
    return [tc for tc in EVALUATION_TEST_CASES if tc.query_type == query_type]


def get_all_test_cases():
    """Get all test cases."""
    return EVALUATION_TEST_CASES


if __name__ == "__main__":
    print("=" * 60)
    print("EVALUATION TEST SUITE")
    print("=" * 60)
    print(f"\nTotal test cases: {len(EVALUATION_TEST_CASES)}")

    for query_type in QueryType:
        cases = get_test_cases_by_type(query_type)
        print(f"  {query_type.value}: {len(cases)} cases")

    print("\n" + "=" * 60)
    print("SAMPLE TEST CASES")
    print("=" * 60)

    for i, tc in enumerate(EVALUATION_TEST_CASES[:3], 1):
        print(f"\n[{i}] {tc.query_type.value.upper()}")
        print(f"    Query: {tc.query}")
        print(f"    Expected: {', '.join(tc.expected_keywords)}")

    print("\n" + "=" * 60)
