"""Final evaluation with Ollama - 3 key queries to verify system works."""

import sys
import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline import MultimodalRAGPipeline
import os

# Critical test queries
TEST_QUERIES = [
    {
        "query": "What is a RAG system?",
        "type": "factual",
        "expected_terms": ["retrieval", "generation", "augmented"],
    },
    {
        "query": "What is Qdrant?",
        "type": "factual",
        "expected_terms": ["vector", "database"],
    },
    {
        "query": "What is a knowledge graph?",
        "type": "factual",
        "expected_terms": ["entities", "relationships"],
    },
]

def check_answer_quality(answer, expected_terms):
    """Simple check if answer contains expected terms."""
    answer_lower = answer.lower()
    found = sum(1 for term in expected_terms if term.lower() in answer_lower)
    coverage = found / len(expected_terms) if expected_terms else 0
    return coverage >= 0.5, coverage

def main():
    print("=" * 60)
    print("FINAL EVALUATION WITH OLLAMA (No API Key Required)")
    print("=" * 60)

    print("\n[1/3] Initializing pipeline...")
    try:
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
        print("   [PASS] Pipeline initialized with Ollama")
    except Exception as e:
        print(f"   [FAIL] Failed to initialize pipeline: {e}")
        return 1

    print("\n[2/3] Running queries...")
    results = []
    passed = 0
    failed = 0

    for i, test in enumerate(TEST_QUERIES, 1):
        print(f"\n   Query {i}/{len(TEST_QUERIES)}: {test['query']}")

        try:
            response = pipeline.query(test['query'])

            answer_valid, coverage = check_answer_quality(
                response.answer,
                test['expected_terms']
            )

            if answer_valid:
                status = "PASS"
                passed += 1
            else:
                status = "FAIL"
                failed += 1

            print(f"   [{status}] Coverage: {coverage*100:.0f}%")
            print(f"   Latency: {response.metrics.get('total_time_ms', 0):.0f}ms")
            print(f"   Answer preview: {response.answer[:80]}...")

            results.append({
                "query": test['query'],
                "answer": response.answer,
                "expected_terms": test['expected_terms'],
                "coverage": coverage,
                "passed": answer_valid,
                "metrics": response.metrics,
            })

        except Exception as e:
            print(f"   [FAIL] Query error: {e}")
            failed += 1
            results.append({
                "query": test['query'],
                "error": str(e),
                "passed": False,
            })

    print("\n[3/3] Saving results...")

    report = {
        "timestamp": datetime.now().isoformat(),
        "llm_provider": "ollama",
        "llm_model": "llama3.2",
        "total_queries": len(TEST_QUERIES),
        "passed": passed,
        "failed": failed,
        "pass_rate": passed / len(TEST_QUERIES) if TEST_QUERIES else 0,
        "avg_latency_ms": sum(r.get('metrics', {}).get('total_time_ms', 0)
                             for r in results) / len(results) if results else 0,
        "avg_coverage": sum(r.get('coverage', 0) for r in results) / len(results) if results else 0,
        "results": results,
    }

    logs_dir = project_root / "logs" / "eval"
    logs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = logs_dir / f"final_evaluation_{timestamp}.json"

    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"   [PASS] Report saved: {report_path}")

    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    print(f"Total queries: {len(TEST_QUERIES)}")
    print(f"Passed: {passed} ({passed/len(TEST_QUERIES)*100:.0f}%)")
    print(f"Failed: {failed}")
    print(f"Avg latency: {report['avg_latency_ms']:.0f}ms")
    print(f"Avg coverage: {report['avg_coverage']*100:.0f}%")
    print(f"\nReport: {report_path}")

    return 0 if passed >= 2 else 1  # At least 2/3 must pass

if __name__ == "__main__":
    exit(main())
