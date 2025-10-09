"""Main CLI entry point for Multimodal RAG System."""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import MultimodalRAGPipeline

load_dotenv()


def main():
    """Run the CLI interface."""
    print("=" * 60)
    print("MULTIMODAL ENTERPRISE RAG SYSTEM")
    print("=" * 60)

    # Initialize pipeline with Ollama (no API key needed)
    print("\nInitializing pipeline...")
    pipeline = MultimodalRAGPipeline(
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", "password123"),
        qdrant_host=os.getenv("QDRANT_HOST", "localhost"),
        qdrant_port=int(os.getenv("QDRANT_PORT", "6333")),
        llm_provider="ollama",
        llm_model="llama3.2",
        enable_evaluation=True,
    )

    print("Pipeline initialized with Ollama (llama3.2)")
    print("\nCommands:")
    print("  query <question>  - Ask a question")
    print("  ingest <path>     - Ingest file or directory")
    print("  stats             - Show system statistics")
    print("  exit              - Quit")
    print("\n" + "=" * 60)

    while True:
        try:
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("Goodbye!")
                break

            elif user_input.lower() == "stats":
                stats = pipeline.get_stats()
                print("\n[GRAPH DATABASE]")
                print(f"  Nodes: {stats['graph'].get('total_nodes', 0)}")
                print(f"  Relationships: {stats['graph'].get('total_relationships', 0)}")
                print("\n[VECTOR DATABASE]")
                print(f"  Vectors: {stats['vector'].get('total_vectors', 0)}")
                print(f"  Vector size: {stats['vector'].get('vector_size', 0)}")

            elif user_input.lower().startswith("ingest "):
                path = user_input[7:].strip()
                print(f"\nIngesting: {path}")
                try:
                    result = pipeline.ingest_file(path)
                    print(f"[SUCCESS] Ingested {result.get('chunks', 0)} chunks")
                except Exception as e:
                    print(f"[ERROR] {e}")

            elif user_input.lower().startswith("query "):
                question = user_input[6:].strip()
                print(f"\nQuery: {question}")
                print("Searching...")

                try:
                    response = pipeline.query(question)
                    print(f"\n[ANSWER]")
                    print(response.answer)
                    print(f"\n[METRICS]")
                    print(f"  Retrieval time: {response.metrics.get('retrieval_time_ms', 0):.0f}ms")
                    print(f"  Generation time: {response.metrics.get('generation_time_ms', 0):.0f}ms")
                    print(f"  Total time: {response.metrics.get('total_time_ms', 0):.0f}ms")
                    print(f"  Sources used: {len(response.contexts)}")
                except Exception as e:
                    print(f"[ERROR] {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("Unknown command. Try: query, ingest, stats, or exit")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

    pipeline.close()


if __name__ == "__main__":
    main()
