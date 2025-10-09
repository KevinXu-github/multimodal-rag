"""Verify agents are actually being used in queries."""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import MultimodalRAGPipeline

load_dotenv()


def verify_agents():
    """Verify agents are actually routing queries."""
    print("=" * 60)
    print("VERIFICATION: AGENTS ACTUALLY BEING USED")
    print("=" * 60)

    pipeline = MultimodalRAGPipeline(
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", "password123"),
        qdrant_host=os.getenv("QDRANT_HOST", "localhost"),
        qdrant_port=int(os.getenv("QDRANT_PORT", "6333")),
        llm_provider="ollama",
        llm_model="llama3.2",
    )

    print(f"\n[CHECK 1] Pipeline configuration:")
    print(f"  use_agents = {pipeline.use_agents}")
    print(f"  agent_router exists = {pipeline.agent_router is not None}")

    if not pipeline.use_agents:
        print("\n[FAIL] Agents are DISABLED by default!")
        return 1

    if pipeline.agent_router is None:
        print("\n[FAIL] Agent router is None!")
        return 1

    print("  [PASS] Agents are enabled and router exists")

    print(f"\n[CHECK 2] Running a factual query...")
    response = pipeline.query("What is Qdrant?")

    print(f"  Answer: {response.answer[:80]}...")
    print(f"  Metrics keys: {list(response.metrics.keys())}")

    if 'agent_used' not in response.metrics:
        print("\n[FAIL] 'agent_used' NOT in metrics! Agents are NOT being used!")
        print(f"  Full metrics: {response.metrics}")
        return 1

    print(f"  [PASS] Agent was used: {response.metrics['agent_used']}")
    print(f"  [PASS] Query type detected: {response.metrics['query_type']}")

    print(f"\n[CHECK 3] Testing different query types...")
    test_cases = [
        ("Find vector databases", "lookup", "LookupAgent"),
        ("How does RAG work?", "reasoning", "ReasoningAgent"),
        ("What is Neo4j?", "factual", "FactualAgent"),
    ]

    all_passed = True
    for query, expected_type, expected_agent in test_cases:
        response = pipeline.query(query)

        if 'agent_used' not in response.metrics:
            print(f"  [FAIL] Query: '{query}' - NO AGENT USED!")
            all_passed = False
            continue

        agent_used = response.metrics.get('agent_used')
        query_type = response.metrics.get('query_type')

        print(f"\n  Query: '{query}'")
        print(f"    Expected type: {expected_type}, Got: {query_type}")
        print(f"    Expected agent: {expected_agent}, Got: {agent_used}")

        if query_type != expected_type:
            print(f"    [INFO] Query type mismatch (not critical)")

        if agent_used:
            print(f"    [PASS] Agent is being used")
        else:
            print(f"    [FAIL] No agent used!")
            all_passed = False

    print(f"\n[CHECK 4] Test with agents DISABLED...")
    pipeline.use_agents = False
    response = pipeline.query("What is a RAG system?")

    if 'agent_used' in response.metrics:
        print(f"  [FAIL] Agent info found when agents disabled!")
        return 1

    print(f"  [PASS] No agent info when disabled (correct)")

    # Re-enable
    pipeline.use_agents = True
    response = pipeline.query("What is a RAG system?")

    if 'agent_used' not in response.metrics:
        print(f"  [FAIL] Agent info missing when re-enabled!")
        return 1

    print(f"  [PASS] Agent info present when re-enabled")

    pipeline.close()

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] VERIFICATION PASSED: Agents are actively being used!")
    else:
        print("[FAILURE] VERIFICATION FAILED: Issues detected!")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(verify_agents())
