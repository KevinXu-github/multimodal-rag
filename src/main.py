"""Main entry point for the RAG system."""

import os
from pathlib import Path
from dotenv import load_dotenv

from .pipeline import MultimodalRAGPipeline

load_dotenv()


def main():
    """Run the RAG system."""
    llm_provider = os.getenv("LLM_PROVIDER", "google")

    if llm_provider == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
    elif llm_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
    else:
        api_key = os.getenv("ANTHROPIC_API_KEY")

    pipeline = MultimodalRAGPipeline(
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", "password123"),
        qdrant_host=os.getenv("QDRANT_HOST", "localhost"),
        qdrant_port=int(os.getenv("QDRANT_PORT", "6333")),
        llm_provider=llm_provider,
        llm_model=os.getenv("LLM_MODEL", "gemini-1.5-flash"),
        llm_api_key=api_key,
        embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
    )

    print("Initializing RAG system...")
    pipeline.initialize()

    print("\nRAG System Ready!")
    print("\nCommands:")
    print("  ingest <file_or_directory> - Ingest files")
    print("  query <question> - Ask a question")
    print("  stats - Show system statistics")
    print("  exit - Quit")

    while True:
        try:
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                break

            if user_input.startswith("ingest "):
                path_str = user_input[7:].strip()
                path = Path(path_str)

                if path.is_file():
                    success = pipeline.ingest_file(path)
                    print(f"{'Success' if success else 'Failed'} ingesting {path}")
                elif path.is_dir():
                    stats = pipeline.ingest_directory(path)
                    print(f"Ingested {stats['successful']}/{stats['total']} files")
                else:
                    print(f"Path not found: {path}")

            elif user_input.startswith("query "):
                question = user_input[6:].strip()
                response = pipeline.query(question)

                print(f"\nQuestion: {response.question}")
                print(f"\nAnswer: {response.answer}")
                print(f"\nConfidence: {response.confidence:.2f}")
                print(f"Time: {response.metrics.get('total_time_ms', 0):.0f}ms")

            elif user_input == "stats":
                stats = pipeline.get_stats()
                print("\nSystem Statistics:")
                print(f"  Graph: {stats['graph']}")
                print(f"  Vector: {stats['vector']}")

            else:
                print("Unknown command. Use: ingest, query, stats, or exit")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

    pipeline.close()
    print("Goodbye!")


if __name__ == "__main__":
    main()
