"""Simple standalone test for query expansion without heavy dependencies."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "retrieval"))

# Import directly
from query_expander import QueryExpander, MultiQueryGenerator


def test_query_expansion():
    """Test basic query expansion with assertions."""
    print("\n" + "=" * 60)
    print("TESTING QUERY EXPANSION")
    print("=" * 60)

    expander = QueryExpander()

    # Test 1: Synonym expansion
    query = "find document about system error"
    expanded = expander.expand(query)

    print(f"\nTest 1: Original: {query}")
    print(f"Expanded to {len(expanded)} queries")

    assert len(expanded) > 1, "FAIL: Should generate multiple queries"
    assert query in expanded, "FAIL: Should include original"
    assert any("locate" in q or "search" in q for q in expanded), "FAIL: Should have synonyms"
    print("[PASS] Synonym expansion works")

    # Test 2: Question reformulation
    query2 = "What is a knowledge graph?"
    expanded2 = expander.expand(query2)

    print(f"\nTest 2: Original: {query2}")
    print(f"Expanded to {len(expanded2)} queries")

    assert len(expanded2) > 1, "FAIL: Should generate variations"
    assert any("definition" in q.lower() for q in expanded2), "FAIL: Should reformulate"
    print("[PASS] Question reformulation works")

    # Test 3: Query rewriting
    query3 = "What is a vector database?"
    rewritten = expander.rewrite(query3, "factual")

    print(f"\nTest 3: Original: {query3}")
    print(f"Rewritten: {rewritten}")

    assert isinstance(rewritten, str), "FAIL: Should return string"
    assert len(rewritten) > 0, "FAIL: Should not be empty"
    assert "vector database" in rewritten.lower(), "FAIL: Should preserve key terms"
    print("[PASS] Query rewriting works")

    # Test 4: Multi-query generation
    multi_gen = MultiQueryGenerator()
    query4 = "How do evaluation metrics work?"
    multi_queries = multi_gen.generate_multi_queries(query4, num_queries=3)

    print(f"\nTest 4: Original: {query4}")
    print(f"Generated {len(multi_queries)} variations")

    assert len(multi_queries) >= 3, "FAIL: Should generate multiple queries"
    assert all(isinstance(q, str) for q in multi_queries), "FAIL: All should be strings"
    assert len(set(multi_queries)) > 1, "FAIL: Should be diverse"
    print("[PASS] Multi-query generation works")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        success = test_query_expansion()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
