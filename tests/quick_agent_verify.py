"""Quick verification that agents are actually being used."""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import MultimodalRAGPipeline

load_dotenv()

print("=" * 60)
print("QUICK AGENT VERIFICATION")
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

print(f"\n[1] Pipeline Config:")
print(f"    use_agents = {pipeline.use_agents}")
print(f"    agent_router = {pipeline.agent_router is not None}")

if pipeline.use_agents and pipeline.agent_router:
    print("    [PASS]")
else:
    print("    [FAIL]")
    exit(1)

print(f"\n[2] Run ONE query and check metrics...")
response = pipeline.query("What is Qdrant?")

print(f"    Metrics: {list(response.metrics.keys())}")

if 'agent_used' in response.metrics and 'query_type' in response.metrics:
    print(f"    agent_used = {response.metrics['agent_used']}")
    print(f"    query_type = {response.metrics['query_type']}")
    print("    [PASS] Agents ARE being used!")
else:
    print("    [FAIL] Agents NOT being used!")
    print(f"    Full metrics: {response.metrics}")
    exit(1)

print(f"\n[3] Disable agents and test...")
pipeline.use_agents = False
response2 = pipeline.query("What is a RAG system?")

if 'agent_used' not in response2.metrics:
    print("    [PASS] No agent info when disabled")
else:
    print("    [FAIL] Agent info present when should be disabled")
    exit(1)

pipeline.close()

print("\n" + "=" * 60)
print("[SUCCESS] Agents are working correctly!")
print("=" * 60)
