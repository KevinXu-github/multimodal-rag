"""Test query expansion and rewriting functionality with proper assertions."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retrieval.query_expander import QueryExpander, MultiQueryGenerator


def test_query_expansion():
    """Test basic query expansion with assertions."""
    expander = QueryExpander()

    # Test 1: Synonym expansion
    query = "find document about system error"
    expanded = expander.expand(query)

    print("\n" + "=" * 60)
    print("TEST 1: Query Expansion with Synonyms")
    print("=" * 60)
    print(f"Original: {query}")
    print(f"Expanded queries ({len(expanded)}):")
    for i, exp_query in enumerate(expanded, 1):
        print(f"  {i}. {exp_query}")

    # Assertions
    assert len(expanded) > 1, "Should generate multiple expanded queries"
    assert query in expanded, "Should include original query"
    assert any("locate" in q or "search" in q or "retrieve" in q for q in expanded), \
        "Should include synonym for 'find'"
    assert any("file" in q or "paper" in q for q in expanded), \
        "Should include synonym for 'document'"
    print("[PASS] Synonym expansion works correctly")

    # Test 2: Question reformulation
    query2 = "What is a knowledge graph?"
    expanded2 = expander.expand(query2)

    print("\n" + "=" * 60)
    print("TEST 2: Question Reformulation")
    print("=" * 60)
    print(f"Original: {query2}")
    print(f"Expanded queries ({len(expanded2)}):")
    for i, exp_query in enumerate(expanded2, 1):
        print(f"  {i}. {exp_query}")

    # Assertions
    assert len(expanded2) > 1, "Should generate multiple variations"
    assert any("definition" in q.lower() for q in expanded2), \
        "Should include reformulated version with 'definition'"
    print("[PASS] Question reformulation works correctly")

    # Test 3: How-to question
    query3 = "How to create a database?"
    expanded3 = expander.expand(query3)

    print("\n" + "=" * 60)
    print("TEST 3: How-To Question")
    print("=" * 60)
    print(f"Original: {query3}")
    print(f"Expanded queries ({len(expanded3)}):")
    for i, exp_query in enumerate(expanded3, 1):
        print(f"  {i}. {exp_query}")

    # Assertions
    assert len(expanded3) > 1, "Should generate multiple variations"
    assert any("steps" in q.lower() or "process" in q.lower() for q in expanded3), \
        "Should include reformulated version with 'steps' or 'process'"
    print("[PASS] How-to question expansion works correctly")


def test_query_rewriting():
    """Test query rewriting for different types with assertions."""
    expander = QueryExpander()

    print("\n" + "=" * 60)
    print("TEST 4: Type-Specific Query Rewriting")
    print("=" * 60)

    test_cases = [
        ("What is a vector database?", "factual", ["definition", "vector database"]),
        ("Find all documents about machine learning", "lookup", ["machine learning"]),
        ("Summarize the main requirements", "summarization", ["main", "requirements"]),
        ("Why does the system need a knowledge graph?", "reasoning", ["knowledge graph"]),
    ]

    for query, query_type, expected_keywords in test_cases:
        rewritten = expander.rewrite(query, query_type)
        print(f"\n{query_type.upper()}:")
        print(f"  Original:  {query}")
        print(f"  Rewritten: {rewritten}")

        # Assertions
        assert isinstance(rewritten, str), "Should return a string"
        assert len(rewritten) > 0, "Should not be empty"
        for keyword in expected_keywords:
            assert keyword.lower() in rewritten.lower(), \
                f"Rewritten query should contain '{keyword}'"
        print(f"  [PASS] {query_type} rewriting works")


def test_multi_query_generation():
    """Test multi-query generation with assertions."""
    multi_gen = MultiQueryGenerator()

    print("\n" + "=" * 60)
    print("TEST 5: Multi-Query Generation")
    print("=" * 60)

    query = "What are the evaluation metrics and how are they tracked?"
    num_queries = 4
    multi_queries = multi_gen.generate_multi_queries(query, num_queries=num_queries)

    print(f"Original: {query}")
    print(f"\nGenerated {len(multi_queries)} variations:")
    for i, mq in enumerate(multi_queries, 1):
        print(f"  {i}. {mq}")

    # Assertions
    assert isinstance(multi_queries, list), "Should return a list"
    assert len(multi_queries) >= num_queries, f"Should generate at least {num_queries} queries"
    assert all(isinstance(q, str) for q in multi_queries), "All queries should be strings"
    assert all(len(q) > 0 for q in multi_queries), "No empty queries"

    # Check that queries are different
    unique_queries = set(multi_queries)
    assert len(unique_queries) > 1, "Should generate diverse queries"
    print("[PASS] Multi-query generation works correctly")


def run_all_tests():
    """Run all tests with proper error handling."""
    tests = [
        ("Query Expansion", test_query_expansion),
        ("Query Rewriting", test_query_rewriting),
        ("Multi-Query Generation", test_multi_query_generation),
    ]

    passed = 0
    failed = 0

    print("\n" + "=" * 60)
    print("QUERY EXPANSION & REWRITING TEST SUITE")
    print("=" * 60)

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n[FAIL] {test_name}: {e}")
            failed += 1
        except Exception as e:
            print(f"\n[ERROR] {test_name}: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
