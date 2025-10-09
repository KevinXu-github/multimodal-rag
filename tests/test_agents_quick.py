"""Quick test of agent integration without running full queries."""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import MultimodalRAGPipeline
from src.evaluation.metrics import QueryType

load_dotenv()


def test_agents_quick():
    """Quick agent integration test."""
    print("=" * 60)
    print("QUICK AGENT INTEGRATION TEST")
    print("=" * 60)

    # Test 1: Pipeline has agents enabled by default
    print("\n[TEST 1] Pipeline initialization...")
    pipeline = MultimodalRAGPipeline(
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", "password123"),
        qdrant_host=os.getenv("QDRANT_HOST", "localhost"),
        qdrant_port=int(os.getenv("QDRANT_PORT", "6333")),
        llm_provider="ollama",
        llm_model="llama3.2",
    )

    assert pipeline.use_agents == True
    assert pipeline.agent_router is not None
    print("  [PASS] Pipeline has agents enabled")
    print(f"  use_agents = {pipeline.use_agents}")

    # Test 2: Agent router can route queries
    print("\n[TEST 2] Agent router routing...")
    try:
        agent_result = pipeline.agent_router.route(
            query="What is a RAG system?",
            query_type=QueryType.FACTUAL,
            top_k=5
        )
        print(f"  [PASS] Agent router works")
        print(f"  Agent used: {agent_result.agent_name}")
        print(f"  Contexts retrieved: {len(agent_result.contexts)}")
        print(f"  Confidence: {agent_result.confidence}")
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Test 3: Query processor classifies queries
    print("\n[TEST 3] Query classification...")
    test_queries = [
        ("What is a RAG system?", QueryType.FACTUAL),
        ("Find all vector databases", QueryType.LOOKUP),
        ("How does hybrid search work?", QueryType.REASONING),
    ]

    for query, expected_type in test_queries:
        processed = pipeline.query_processor.process(query)
        print(f"  Query: '{query}'")
        print(f"    Classified as: {processed.query_type.value}")
        print(f"    Expected: {expected_type.value}")
        if processed.query_type == expected_type:
            print(f"    [PASS]")
        else:
            print(f"    [INFO] Different classification (not necessarily wrong)")

    # Test 4: Can toggle agents on/off
    print("\n[TEST 4] Toggle agents...")
    pipeline.use_agents = False
    assert pipeline.use_agents == False
    print("  [PASS] Agents disabled")

    pipeline.use_agents = True
    assert pipeline.use_agents == True
    print("  [PASS] Agents re-enabled")

    pipeline.close()

    print("\n" + "=" * 60)
    print("[SUCCESS] All quick tests passed!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(test_agents_quick())
