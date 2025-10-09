"""Run comprehensive evaluation of the RAG system."""

import sys
import logging
import os
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / ".env")

from src.evaluation.evaluator import RAGEvaluator, TestCase
from src.evaluation.metrics import QueryType, DEFAULT_CRITERIA
from src.pipeline import MultimodalRAGPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Test cases
EVALUATION_TEST_CASES = [
    # FACTUAL QUERIES (3 cases)
    TestCase(
        query="What is a multimodal RAG system?",
        query_type=QueryType.FACTUAL,
        expected_answer="A multimodal RAG system combines retrieval and generation across text, images, and audio.",
    ),
    TestCase(
        query="What is the purpose of a knowledge graph?",
        query_type=QueryType.FACTUAL,
        expected_answer="A knowledge graph structures entities and relationships for better information retrieval.",
    ),
    TestCase(
        query="What is vector search?",
        query_type=QueryType.FACTUAL,
        expected_answer="Vector search uses semantic embeddings to find similar content based on meaning.",
    ),

    # LOOKUP QUERIES (3 cases)
    TestCase(
        query="Find documents about machine learning",
        query_type=QueryType.LOOKUP,
    ),
    TestCase(
        query="Show me all PDF files in the system",
        query_type=QueryType.LOOKUP,
    ),
    TestCase(
        query="Get information about data preprocessing",
        query_type=QueryType.LOOKUP,
    ),

    # SUMMARIZATION QUERIES (3 cases)
    TestCase(
        query="Summarize all documents about AI",
        query_type=QueryType.SUMMARIZATION,
    ),
    TestCase(
        query="Give me an overview of the main topics in the knowledge base",
        query_type=QueryType.SUMMARIZATION,
    ),
    TestCase(
        query="What are the key concepts covered in the ingested documents?",
        query_type=QueryType.SUMMARIZATION,
    ),

    # SEMANTIC LINKAGE QUERIES (3 cases)
    TestCase(
        query="How are machine learning and neural networks related?",
        query_type=QueryType.SEMANTIC_LINKAGE,
    ),
    TestCase(
        query="What connects data preprocessing and model training?",
        query_type=QueryType.SEMANTIC_LINKAGE,
    ),
    TestCase(
        query="Show the relationship between embeddings and vector search",
        query_type=QueryType.SEMANTIC_LINKAGE,
    ),

    # REASONING QUERIES (3 cases)
    TestCase(
        query="Why would someone use a hybrid search approach?",
        query_type=QueryType.REASONING,
    ),
    TestCase(
        query="What are the advantages of multimodal systems over text-only RAG?",
        query_type=QueryType.REASONING,
    ),
    TestCase(
        query="How does query expansion improve retrieval quality?",
        query_type=QueryType.REASONING,
    ),
]


def run_evaluation(use_agents: bool = True, use_deepeval: bool = False):
    """Run evaluation suite on the RAG pipeline."""

    logger.info("=" * 60)
    logger.info("MULTIMODAL RAG EVALUATION")
    logger.info("=" * 60)
    logger.info(f"Test cases: {len(EVALUATION_TEST_CASES)}")
    logger.info(f"Using agents: {use_agents}")
    logger.info(f"Using DeepEval: {use_deepeval}")
    logger.info("=" * 60)

    # Initialize pipeline
    try:
        logger.info("Initializing RAG pipeline...")
        pipeline = MultimodalRAGPipeline(
            neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
            neo4j_password=os.getenv("NEO4J_PASSWORD", "password123"),
            qdrant_host=os.getenv("QDRANT_HOST", "localhost"),
            qdrant_port=int(os.getenv("QDRANT_PORT", "6333")),
        )
        pipeline.use_agents = use_agents
        logger.info("Pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}", exc_info=True)
        return

    # Initialize evaluator
    evaluator = RAGEvaluator(
        criteria=DEFAULT_CRITERIA,
        use_deepeval=use_deepeval
    )

    # Run evaluation
    results = []
    for i, test_case in enumerate(EVALUATION_TEST_CASES, 1):
        logger.info("")
        logger.info(f"[{i}/{len(EVALUATION_TEST_CASES)}] Testing: {test_case.query}")
        logger.info(f"Type: {test_case.query_type.value}")

        try:
            # Query the pipeline
            response = pipeline.query(test_case.query)

            # Extract data from response (RAGResponse is a dataclass)
            actual_answer = response.answer or ""
            retrieved_contexts = response.contexts or []
            retrieval_time_ms = response.metrics.get("retrieval_time_ms", 0)
            generation_time_ms = response.metrics.get("generation_time_ms", 0)

            # Evaluate
            result = evaluator.evaluate_response(
                query=test_case.query,
                query_type=test_case.query_type,
                actual_answer=actual_answer,
                retrieved_contexts=retrieved_contexts,
                expected_answer=test_case.expected_answer,
                retrieval_time_ms=retrieval_time_ms,
                generation_time_ms=generation_time_ms,
            )

            results.append(result)

            # Log result
            status = "PASS" if result.passed else "FAIL"
            logger.info(f"Status: {status}")
            logger.info(f"Latency: {result.latency_ms:.0f}ms")

            if not result.passed:
                logger.warning(f"Failure reasons: {', '.join(result.failure_reasons)}")

            # Log key metrics
            for metric_type, value in result.metrics.items():
                logger.info(f"  {metric_type.value}: {value:.3f}")

        except Exception as e:
            logger.error(f"Error evaluating test case: {e}", exc_info=True)
            continue

    # Generate report
    logger.info("")
    logger.info("=" * 60)
    logger.info("EVALUATION REPORT")
    logger.info("=" * 60)

    report = evaluator.generate_report(results)

    # Print summary
    summary = report.get("summary", {})
    logger.info(f"Total queries: {summary.get('total_queries', 0)}")
    logger.info(f"Passed: {summary.get('passed', 0)}")
    logger.info(f"Failed: {summary.get('failed', 0)}")
    logger.info(f"Pass rate: {summary.get('pass_rate', 0):.1%}")

    # Print metrics
    logger.info("")
    logger.info("AVERAGE METRICS:")
    metrics = report.get("metrics", {})
    for metric_name, value in metrics.items():
        logger.info(f"  {metric_name}: {value:.3f}")

    # Print by query type
    logger.info("")
    logger.info("BY QUERY TYPE:")
    by_type = report.get("by_query_type", {})
    for query_type, stats in by_type.items():
        logger.info(f"  {query_type}:")
        logger.info(f"    Pass rate: {stats.get('pass_rate', 0):.1%} ({stats.get('passed', 0)}/{stats.get('total', 0)})")
        logger.info(f"    Avg latency: {stats.get('avg_latency_ms', 0):.0f}ms")

    # Save report to file
    output_dir = project_root / "logs" / "eval"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"evaluation_report_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    logger.info("")
    logger.info(f"Report saved to: {output_file}")
    logger.info("=" * 60)

    return report


if __name__ == "__main__":
    # Parse command line args
    use_agents = "--no-agents" not in sys.argv
    use_deepeval = "--deepeval" in sys.argv

    run_evaluation(use_agents=use_agents, use_deepeval=use_deepeval)
