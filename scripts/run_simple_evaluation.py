"""Simple evaluation script that actually runs queries and measures results."""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline import MultimodalRAGPipeline
from dotenv import load_dotenv

# Load environment variables
load_dotenv(project_root / ".env")

# Test queries covering different types
TEST_QUERIES = [
    {
        "query": "What is a RAG system?",
        "type": "factual",
        "expected_terms": ["retrieval", "generation", "augmented"],
    },
    {
        "query": "What are the key components of RAG?",
        "type": "factual",
        "expected_terms": ["knowledge base", "retrieval", "generation"],
    },
    {
        "query": "What is Qdrant?",
        "type": "factual",
        "expected_terms": ["vector", "database", "similarity"],
    },
    {
        "query": "What distance metrics are used in vector search?",
        "type": "lookup",
        "expected_terms": ["cosine", "euclidean", "dot product"],
    },
    {
        "query": "What is a knowledge graph?",
        "type": "factual",
        "expected_terms": ["entities", "relationships", "nodes", "edges"],
    },
]


def evaluate_answer(answer: str, expected_terms: list) -> dict:
    """Simple evaluation based on term presence."""
    answer_lower = answer.lower()

    # Check for expected terms
    terms_found = [term for term in expected_terms if term.lower() in answer_lower]
    term_coverage = len(terms_found) / len(expected_terms) if expected_terms else 0

    # Basic quality checks
    is_empty = len(answer.strip()) == 0
    is_too_short = len(answer.split()) < 10
    has_error = "error" in answer_lower or "sorry" in answer_lower

    return {
        "term_coverage": term_coverage,
        "terms_found": terms_found,
        "terms_missing": [t for t in expected_terms if t not in terms_found],
        "word_count": len(answer.split()),
        "is_empty": is_empty,
        "is_too_short": is_too_short,
        "has_error": has_error,
        "passed": term_coverage >= 0.5 and not is_empty and not has_error,
    }


def main():
    print("\n" + "=" * 70)
    print("SIMPLE RAG SYSTEM EVALUATION")
    print("=" * 70)

    # Initialize pipeline
    print("\n[1/3] Initializing pipeline...")
    try:
        pipeline = MultimodalRAGPipeline(
            neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
            neo4j_password=os.getenv("NEO4J_PASSWORD", "password123"),
            qdrant_host=os.getenv("QDRANT_HOST", "localhost"),
            qdrant_port=int(os.getenv("QDRANT_PORT", "6333")),
        )
        print("   Pipeline initialized successfully!")
    except Exception as e:
        print(f"   ERROR: Failed to initialize pipeline: {e}")
        return False

    # Run test queries
    print(f"\n[2/3] Running {len(TEST_QUERIES)} test queries...")
    results = []

    for i, test_case in enumerate(TEST_QUERIES, 1):
        print(f"\n   Query {i}/{len(TEST_QUERIES)}: {test_case['query']}")
        print(f"   Type: {test_case['type']}")

        try:
            start_time = time.time()
            response = pipeline.query(test_case['query'])
            latency_ms = (time.time() - start_time) * 1000

            # Extract answer
            answer = response.answer if hasattr(response, 'answer') else str(response)
            contexts = response.contexts if hasattr(response, 'contexts') else []

            # Evaluate
            eval_result = evaluate_answer(answer, test_case['expected_terms'])
            eval_result.update({
                "query": test_case['query'],
                "query_type": test_case['type'],
                "answer": answer,
                "latency_ms": latency_ms,
                "context_count": len(contexts),
            })

            results.append(eval_result)

            # Print result
            status = "[PASS]" if eval_result['passed'] else "[FAIL]"
            print(f"   {status} Latency: {latency_ms:.0f}ms | Coverage: {eval_result['term_coverage']:.0%}")
            if eval_result['terms_missing']:
                print(f"   Missing terms: {', '.join(eval_result['terms_missing'])}")

        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
            results.append({
                "query": test_case['query'],
                "query_type": test_case['type'],
                "passed": False,
                "error": str(e),
            })

    # Generate report
    print(f"\n[3/3] Generating report...")

    passed = sum(1 for r in results if r.get('passed', False))
    failed = len(results) - passed
    pass_rate = passed / len(results) if results else 0

    avg_latency = sum(r.get('latency_ms', 0) for r in results if 'latency_ms' in r) / len(results) if results else 0
    avg_coverage = sum(r.get('term_coverage', 0) for r in results) / len(results) if results else 0

    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_queries": len(results),
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "avg_latency_ms": avg_latency,
            "avg_term_coverage": avg_coverage,
        },
        "results": results,
    }

    # Save report
    output_dir = project_root / "logs" / "eval"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"simple_evaluation_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print("EVALUATION RESULTS")
    print("=" * 70)
    print(f"Total Queries: {len(results)}")
    print(f"Passed: {passed} ({pass_rate:.0%})")
    print(f"Failed: {failed}")
    print(f"Average Latency: {avg_latency:.0f}ms")
    print(f"Average Term Coverage: {avg_coverage:.0%}")
    print(f"\nReport saved to: {output_file}")
    print("=" * 70)

    return pass_rate >= 0.6  # 60% pass rate threshold


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
