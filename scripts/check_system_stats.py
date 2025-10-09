"""Check current system statistics."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline import MultimodalRAGPipeline
import os

print("=" * 60)
print("SYSTEM STATUS CHECK")
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

stats = pipeline.get_stats()

print("\n[GRAPH DATABASE - NEO4J]")
print(f"  Total nodes: {stats['graph'].get('total_nodes', 0)}")
print(f"  Total relationships: {stats['graph'].get('total_relationships', 0)}")
print(f"  Entity types: {stats['graph'].get('entity_count_by_type', {})}")

print("\n[VECTOR DATABASE - QDRANT]")
print(f"  Total vectors: {stats['vector'].get('total_vectors', 0)}")
print(f"  Vector size: {stats['vector'].get('vector_size', 0)}")
print(f"  Distance metric: {stats['vector'].get('distance_metric', 'N/A')}")

print("\n[LLM CONFIGURATION]")
print(f"  Provider: ollama (no API key required)")
print(f"  Model: llama3.2")

print("\n[EVALUATION REPORTS]")
logs_dir = project_root / "logs" / "eval"
if logs_dir.exists():
    reports = list(logs_dir.glob("*.json"))
    print(f"  Total reports: {len(reports)}")
    if reports:
        latest = max(reports, key=lambda p: p.stat().st_mtime)
        print(f"  Latest: {latest.name}")

print("\n" + "=" * 60)
print("SYSTEM READY")
print("=" * 60)

pipeline.close()
