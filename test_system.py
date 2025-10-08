"""Simple test script for the RAG system."""

from pathlib import Path
from src.pipeline import MultimodalRAGPipeline
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Multimodal RAG System Test")
print("=" * 60)

# Check environment variables
print("\n1. Checking configuration...")
if not os.getenv("GOOGLE_API_KEY"):
    print("ERROR: GOOGLE_API_KEY not found in .env file")
    print("Please add your API key to .env file")
    exit(1)
print("API key found")

# Initialize pipeline
print("\n2. Initializing pipeline...")
try:
    pipeline = MultimodalRAGPipeline(
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", "password123"),
        qdrant_host=os.getenv("QDRANT_HOST", "localhost"),
        qdrant_port=int(os.getenv("QDRANT_PORT", "6333")),
        llm_provider="google",
        llm_model=os.getenv("LLM_MODEL", "gemini-1.5-flash"),
        llm_api_key=os.getenv("GOOGLE_API_KEY"),
    )
    print("Pipeline created")
except Exception as e:
    print(f"ERROR: Failed to create pipeline: {e}")
    print("\nMake sure Docker services are running:")
    print("  cd infrastructure/docker")
    print("  docker-compose up -d")
    exit(1)

# Initialize databases
print("\n3. Initializing databases...")
try:
    pipeline.initialize()
    print("Databases initialized")
except Exception as e:
    print(f"ERROR: Failed to initialize databases: {e}")
    exit(1)

# Check for test file
print("\n4. Checking for test file...")
test_file = Path("HybridMultiModalChallenge.pdf")
if not test_file.exists():
    print(f"Test file not found: {test_file}")
    print("\nPlease create a test file or use the challenge PDF")
    print("You can also test with any PDF, image, or audio file")

    # Offer to test with query only
    response = input("\nWould you like to test with a query only? (y/n): ")
    if response.lower() == 'y':
        test_query = True
    else:
        pipeline.close()
        exit(0)
else:
    print(f"Found test file: {test_file}")

    # Test ingestion
    print(f"\n5. Testing ingestion with {test_file}...")
    try:
        success = pipeline.ingest_file(test_file)
        if success:
            print(f"Successfully ingested {test_file}")
        else:
            print(f"Failed to ingest {test_file}")
    except Exception as e:
        print(f"ERROR during ingestion: {e}")

    test_query = True

# Test query
if test_query:
    print("\n6. Testing query...")
    test_questions = [
        "What is the main topic?",
        "Summarize the key points",
    ]

    for question in test_questions:
        print(f"\nQuestion: {question}")
        try:
            response = pipeline.query(question)
            print(f"Answer: {response.answer[:200]}...")
            print(f"Confidence: {response.confidence:.2%}")
            print(f"Contexts retrieved: {len(response.contexts)}")
            print(f"Response time: {response.metrics.get('total_time_ms', 0):.0f}ms")
        except Exception as e:
            print(f"ERROR during query: {e}")

# Get stats
print("\n7. System statistics...")
try:
    stats = pipeline.get_stats()
    print(f"Graph entities: {stats['graph'].get('total_entities', 0)}")
    print(f"Graph relationships: {stats['graph'].get('total_relationships', 0)}")
    print(f"Vector documents: {stats['vector'].get('total_vectors', 0)}")
except Exception as e:
    print(f"ERROR getting stats: {e}")

# Cleanup
print("\n8. Cleaning up...")
pipeline.close()
print("Pipeline closed")

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
print("\nNext steps:")
print("  - Run CLI: python -m src.main")
print("  - Run Web UI: streamlit run src/ui/app.py")
print("=" * 60)
