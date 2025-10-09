"""Quick system test to verify all components work."""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import MultimodalRAGPipeline

load_dotenv()


def test_system():
    """Run comprehensive system test."""
    print("=" * 60)
    print("SYSTEM INTEGRATION TEST")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Initialize pipeline
    print("\n[TEST 1] Pipeline initialization...")
    try:
        pipeline = MultimodalRAGPipeline(
            neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
            neo4j_password=os.getenv("NEO4J_PASSWORD", "password123"),
            qdrant_host=os.getenv("QDRANT_HOST", "localhost"),
            qdrant_port=int(os.getenv("QDRANT_PORT", "6333")),
            llm_provider="ollama",
            llm_model="llama3.2",
        )
        print("  [PASS] Pipeline initialized")
        tests_passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        tests_failed += 1
        return

    # Test 2: Check infrastructure
    print("\n[TEST 2] Infrastructure connectivity...")
    try:
        stats = pipeline.get_stats()
        print(f"  Neo4j nodes: {stats['graph'].get('total_nodes', 0)}")
        print(f"  Qdrant vectors: {stats['vector'].get('total_vectors', 0)}")
        print("  [PASS] Infrastructure connected")
        tests_passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        tests_failed += 1

    # Test 3: Query system
    print("\n[TEST 3] Query processing...")
    try:
        response = pipeline.query("What is a RAG system?")
        assert len(response.answer) > 0, "Empty answer"
        print(f"  Answer length: {len(response.answer)} chars")
        print(f"  Latency: {response.metrics.get('total_time_ms', 0):.0f}ms")
        print("  [PASS] Query processed successfully")
        tests_passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        tests_failed += 1

    # Test 4: Vector search
    print("\n[TEST 4] Vector search...")
    try:
        results = pipeline.vector_store.search(
            query="knowledge graph",
            top_k=5
        )
        print(f"  Retrieved {len(results)} results")
        print("  [PASS] Vector search working")
        tests_passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        tests_failed += 1

    # Test 5: Hybrid retrieval
    print("\n[TEST 5] Hybrid retrieval...")
    try:
        search_result = pipeline.search_engine.search(
            query="vector database",
            top_k=5
        )
        print(f"  Retrieved {search_result.total_results} results")
        print(f"  Graph: {search_result.graph_results}, Vector: {search_result.vector_results}, Keyword: {search_result.keyword_results}")
        if search_result.results:
            print(f"  Top result score: {search_result.results[0].score:.3f}")
            print(f"  Methods used: {set(r.retrieval_method for r in search_result.results)}")
        print("  [PASS] Hybrid search working")
        tests_passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        tests_failed += 1

    pipeline.close()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")
    print(f"Total:  {tests_passed + tests_failed}")

    if tests_failed == 0:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print(f"\n[FAILURE] {tests_failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(test_system())
