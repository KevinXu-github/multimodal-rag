"""Quick test that Ollama works with the pipeline."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import ollama

print("Testing Ollama directly...")
try:
    response = ollama.generate(
        model="llama3.2",
        prompt="What is 2+2? Answer in one word.",
        options={"temperature": 0.0, "num_predict": 10}
    )
    print(f"[PASS] Ollama works! Response: {response['response']}")
except Exception as e:
    print(f"[FAIL] Ollama error: {e}")
    sys.exit(1)

print("\nTesting AnswerGenerator with Ollama...")
try:
    from src.generation import AnswerGenerator
    from src.retrieval.hybrid_search import SearchResult

    generator = AnswerGenerator(
        llm_provider="ollama",
        model_name="llama3.2"
    )

    # Create a simple test search result
    test_result = SearchResult(
        content="RAG stands for Retrieval-Augmented Generation. It combines retrieval and generation.",
        source="test",
        score=0.9,
        retrieval_method="vector",
        metadata={"file_name": "test.txt"}
    )

    answer = generator.generate(
        question="What does RAG stand for?",
        search_results=[test_result]
    )

    print(f"[PASS] AnswerGenerator works!")
    print(f"  Answer: {answer.answer[:100]}...")
    print(f"  Confidence: {answer.confidence}")
    print(f"  Generation time: {answer.generation_time_ms:.0f}ms")

except Exception as e:
    print(f"[FAIL] AnswerGenerator error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[PASS] All Ollama tests passed!")
