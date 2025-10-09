"""Quick test with corrected Gemini model."""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.pipeline import MultimodalRAGPipeline

load_dotenv()

print("Testing with Gemini 2.5 Flash...\n")

pipeline = MultimodalRAGPipeline(
    neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
    neo4j_password=os.getenv("NEO4J_PASSWORD", "password123"),
    qdrant_host=os.getenv("QDRANT_HOST", "localhost"),
    qdrant_port=int(os.getenv("QDRANT_PORT", "6333")),
    llm_provider="google",
    llm_model="gemini-2.5-flash",
    llm_api_key=os.getenv("GOOGLE_API_KEY"),
)

print("1. Initializing...")
pipeline.initialize()
print("   Done\n")

print("2. Ingesting PDF...")
pdf_path = Path(__file__).parent.parent / "HybridMultiModalChallenge.pdf"
success = pipeline.ingest_file(pdf_path)
print(f"   {'Success' if success else 'Failed'}\n")

print("3. Querying...")
response = pipeline.query("What are the main requirements of the challenge?")
print(f"   Answer: {response.answer[:200]}...")
print(f"   Confidence: {response.confidence:.2%}")
print(f"   Time: {response.metrics.get('total_time_ms', 0):.0f}ms\n")

print("4. System stats:")
stats = pipeline.get_stats()
print(f"   Entities: {stats['graph'].get('total_entities', 0)}")
print(f"   Vectors: {stats['vector'].get('total_vectors', 0)}")

pipeline.close()
print("\nTest complete!")
