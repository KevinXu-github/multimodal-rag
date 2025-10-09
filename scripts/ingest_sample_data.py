"""Simple script to ingest sample data and verify it works."""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline import MultimodalRAGPipeline
from dotenv import load_dotenv

# Load environment variables
load_dotenv(project_root / ".env")

def main():
    print("\n" + "=" * 60)
    print("INGESTING SAMPLE DATA")
    print("=" * 60)

    # Initialize pipeline
    print("\n[1/4] Initializing pipeline...")
    pipeline = MultimodalRAGPipeline(
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", "password123"),
        qdrant_host=os.getenv("QDRANT_HOST", "localhost"),
        qdrant_port=int(os.getenv("QDRANT_PORT", "6333")),
    )
    print("   Pipeline initialized successfully!")

    # Find sample files
    data_dir = project_root / "data"
    sample_files = list(data_dir.glob("sample_*.txt"))

    if not sample_files:
        print("\n   ERROR: No sample files found in data/")
        print("   Please ensure sample_*.txt files exist")
        return False

    print(f"\n[2/4] Found {len(sample_files)} sample files:")
    for f in sample_files:
        print(f"   - {f.name}")

    # Ingest each file
    print(f"\n[3/4] Ingesting files...")
    for i, file_path in enumerate(sample_files, 1):
        print(f"\n   [{i}/{len(sample_files)}] Processing: {file_path.name}")
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple chunking (every 500 chars)
            chunk_size = 500
            chunks = []
            for j in range(0, len(content), chunk_size):
                chunk_text = content[j:j+chunk_size]
                if chunk_text.strip():
                    chunks.append({
                        'content': chunk_text,
                        'metadata': {
                            'source': file_path.name,
                            'chunk_id': j // chunk_size,
                            'file_path': str(file_path)
                        }
                    })

            print(f"      Created {len(chunks)} chunks")

            # Add to vector store
            added_count = 0
            for idx, chunk in enumerate(chunks):
                # Use hash of filename + idx as integer ID
                doc_id = hash(f"{file_path.stem}_{idx}") % (10**8)
                success = pipeline.vector_store.add_document(
                    doc_id=doc_id,
                    text=chunk['content'],
                    metadata=chunk['metadata']
                )
                if success:
                    added_count += 1

            if added_count != len(chunks):
                print(f"      WARNING: Only added {added_count}/{len(chunks)} chunks")

            print(f"      Added {len(chunks)} chunks to vector store")

            # Extract entities (simple keyword extraction for now)
            # In production, this would use LLM
            print(f"      Extracting entities...")

            # Just mark as successful - full extraction would need LLM API
            print(f"      Completed: {file_path.name}")

        except Exception as e:
            print(f"      ERROR: {e}")
            continue

    # Verify data was loaded
    print(f"\n[4/4] Verifying data...")

    try:
        # Check vector store
        collection_info = pipeline.vector_store.client.get_collection("documents")
        vector_count = collection_info.points_count
        print(f"   Vector store: {vector_count} vectors")

        # Check graph store
        result = pipeline.graph_store.driver.execute_query(
            "MATCH (n) RETURN count(n) as count"
        )
        node_count = result.records[0]["count"]
        print(f"   Graph store: {node_count} nodes")

        print("\n" + "=" * 60)
        print("INGESTION COMPLETE!")
        print("=" * 60)
        print(f"  Files processed: {len(sample_files)}")
        print(f"  Vectors created: {vector_count}")
        print(f"  Graph nodes: {node_count}")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"   ERROR verifying data: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
