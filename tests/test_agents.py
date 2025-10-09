"""Test agent-based retrieval integration."""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import MultimodalRAGPipeline

load_dotenv()


def test_agents():
    """Test agent integration."""
    print("=" * 60)
    print("AGENT INTEGRATION TEST")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Initialize pipeline WITH agents
    print("\n[TEST 1] Pipeline initialization with agents...")
    try:
        pipeline_with_agents = MultimodalRAGPipeline(
            neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
            neo4j_password=os.getenv("NEO4J_PASSWORD", "password123"),
            qdrant_host=os.getenv("QDRANT_HOST", "localhost"),
            qdrant_port=int(os.getenv("QDRANT_PORT", "6333")),
            llm_provider="ollama",
            llm_model="llama3.2",
        )
        assert pipeline_with_agents.use_agents == True, "Agents should be enabled by default"
        print(f"  [PASS] Pipeline initialized (use_agents={pipeline_with_agents.use_agents})")
        tests_passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        tests_failed += 1
        return

    # Test 2: Query with agent routing (factual query)
    print("\n[TEST 2] Factual query with agent routing...")
    try:
        response = pipeline_with_agents.query("What is a RAG system?")
        assert len(response.answer) > 0, "Empty answer"
        assert "agent_used" in response.metrics, "Agent info missing from metrics"
        print(f"  Answer length: {len(response.answer)} chars")
        print(f"  Agent used: {response.metrics.get('agent_used')}")
        print(f"  Query type: {response.metrics.get('query_type')}")
        print(f"  Latency: {response.metrics.get('total_time_ms', 0):.0f}ms")
        print("  [PASS] Agent-based query working")
        tests_passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        tests_failed += 1

    # Test 3: Lookup query
    print("\n[TEST 3] Lookup query with agent routing...")
    try:
        response = pipeline_with_agents.query("Find information about vector databases")
        assert len(response.answer) > 0, "Empty answer"
        print(f"  Agent used: {response.metrics.get('agent_used')}")
        print(f"  Query type: {response.metrics.get('query_type')}")
        print("  [PASS] Lookup agent working")
        tests_passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        tests_failed += 1

    # Test 4: Pipeline WITHOUT agents (hybrid search)
    print("\n[TEST 4] Pipeline with agents disabled...")
    try:
        pipeline_with_agents.use_agents = False
        response = pipeline_with_agents.query("What is Qdrant?")
        assert len(response.answer) > 0, "Empty answer"
        assert "agent_used" not in response.metrics, "Agent info should not be in metrics"
        print(f"  Answer length: {len(response.answer)} chars")
        print(f"  Latency: {response.metrics.get('total_time_ms', 0):.0f}ms")
        print("  [PASS] Hybrid search fallback working")
        tests_passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        tests_failed += 1

    # Test 5: Re-enable agents
    print("\n[TEST 5] Re-enable agents and test...")
    try:
        pipeline_with_agents.use_agents = True
        response = pipeline_with_agents.query("How does hybrid search work?")
        assert len(response.answer) > 0, "Empty answer"
        assert "agent_used" in response.metrics, "Agent info missing"
        print(f"  Agent used: {response.metrics.get('agent_used')}")
        print(f"  Query type: {response.metrics.get('query_type')}")
        print("  [PASS] Agents can be toggled on/off")
        tests_passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        tests_failed += 1

    pipeline_with_agents.close()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")
    print(f"Total:  {tests_passed + tests_failed}")

    if tests_failed == 0:
        print("\n[SUCCESS] All agent tests passed!")
        return 0
    else:
        print(f"\n[FAILURE] {tests_failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(test_agents())
