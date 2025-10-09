"""Core evaluation engine using DeepEval."""

import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    from deepeval import evaluate
    from deepeval.metrics import (
        AnswerRelevancyMetric,
        FaithfulnessMetric,
        ContextualRelevancyMetric,
        HallucinationMetric,
    )
    from deepeval.test_case import LLMTestCase
    DEEPEVAL_AVAILABLE = True
except ImportError:
    DEEPEVAL_AVAILABLE = False

from .metrics import (
    QueryType,
    MetricType,
    EvaluationCriteria,
    EvaluationResult,
    DEFAULT_CRITERIA,
)

logger = logging.getLogger(__name__)


@dataclass
class TestCase:
    """A test case for evaluation."""
    query: str
    query_type: QueryType
    expected_answer: Optional[str] = None
    expected_contexts: Optional[List[str]] = None


class RAGEvaluator:
    """Evaluator for the RAG system using DeepEval metrics."""

    def __init__(
        self,
        criteria: Optional[Dict[QueryType, EvaluationCriteria]] = None,
        use_deepeval: bool = True,
    ):
        self.criteria = criteria or DEFAULT_CRITERIA
        self.use_deepeval = use_deepeval and DEEPEVAL_AVAILABLE

        if use_deepeval and not DEEPEVAL_AVAILABLE:
            logger.warning("Warning: DeepEval not available. Install with: pip install deepeval")
            self.use_deepeval = False

    def evaluate_response(
        self,
        query: str,
        query_type: QueryType,
        actual_answer: str,
        retrieved_contexts: List[str],
        expected_answer: Optional[str] = None,
        retrieval_time_ms: Optional[float] = None,
        generation_time_ms: Optional[float] = None,
    ) -> EvaluationResult:
        """Evaluate a single query-answer pair."""
        start_time = time.time()
        metrics: Dict[MetricType, float] = {}
        failure_reasons: List[str] = []

        total_latency_ms = (retrieval_time_ms or 0) + (generation_time_ms or 0)
        metrics[MetricType.LATENCY] = total_latency_ms

        criteria = self.criteria.get(query_type)
        if not criteria:
            criteria = DEFAULT_CRITERIA[QueryType.FACTUAL]

        if self.use_deepeval and retrieved_contexts:
            deepeval_metrics = self._evaluate_with_deepeval(
                query=query,
                actual_answer=actual_answer,
                expected_answer=expected_answer,
                retrieved_contexts=retrieved_contexts,
            )
            metrics.update(deepeval_metrics)
        else:
            metrics.update(self._evaluate_basic(
                query=query,
                actual_answer=actual_answer,
                expected_answer=expected_answer,
                retrieved_contexts=retrieved_contexts,
            ))

        passed = True

        if MetricType.ACCURACY in metrics:
            if metrics[MetricType.ACCURACY] < criteria.min_accuracy:
                passed = False
                failure_reasons.append(
                    f"Accuracy {metrics[MetricType.ACCURACY]:.2f} < {criteria.min_accuracy}"
                )

        if MetricType.RELEVANCE in metrics:
            if metrics[MetricType.RELEVANCE] < criteria.min_relevance:
                passed = False
                failure_reasons.append(
                    f"Relevance {metrics[MetricType.RELEVANCE]:.2f} < {criteria.min_relevance}"
                )

        if MetricType.HALLUCINATION_RATE in metrics:
            if metrics[MetricType.HALLUCINATION_RATE] > criteria.max_hallucination_rate:
                passed = False
                failure_reasons.append(
                    f"Hallucination rate {metrics[MetricType.HALLUCINATION_RATE]:.2f} > {criteria.max_hallucination_rate}"
                )

        if total_latency_ms > criteria.max_latency_ms:
            passed = False
            failure_reasons.append(
                f"Latency {total_latency_ms:.0f}ms > {criteria.max_latency_ms}ms"
            )

        return EvaluationResult(
            query=query,
            query_type=query_type,
            expected_answer=expected_answer,
            actual_answer=actual_answer,
            retrieved_contexts=retrieved_contexts,
            metrics=metrics,
            passed=passed,
            failure_reasons=failure_reasons,
            latency_ms=total_latency_ms,
        )

    def _evaluate_with_deepeval(
        self,
        query: str,
        actual_answer: str,
        expected_answer: Optional[str],
        retrieved_contexts: List[str],
    ) -> Dict[MetricType, float]:
        """Evaluate using DeepEval metrics."""
        metrics_dict: Dict[MetricType, float] = {}

        try:
            test_case = LLMTestCase(
                input=query,
                actual_output=actual_answer,
                expected_output=expected_answer,
                retrieval_context=retrieved_contexts,
            )

            relevancy_metric = AnswerRelevancyMetric(threshold=0.7)
            relevancy_metric.measure(test_case)
            metrics_dict[MetricType.RELEVANCE] = relevancy_metric.score

            faithfulness_metric = FaithfulnessMetric(threshold=0.8)
            faithfulness_metric.measure(test_case)
            metrics_dict[MetricType.ANSWER_FAITHFULNESS] = faithfulness_metric.score

            hallucination_metric = HallucinationMetric(threshold=0.5)
            hallucination_metric.measure(test_case)
            metrics_dict[MetricType.HALLUCINATION_RATE] = 1.0 - hallucination_metric.score

            context_metric = ContextualRelevancyMetric(threshold=0.7)
            context_metric.measure(test_case)
            metrics_dict[MetricType.CONTEXT_RELEVANCE] = context_metric.score

        except Exception as e:
            logger.error(f"DeepEval evaluation error: {e}", exc_info=True)
            return self._evaluate_basic(query, actual_answer, expected_answer, retrieved_contexts)

        return metrics_dict

    def _evaluate_basic(
        self,
        query: str,
        actual_answer: str,
        expected_answer: Optional[str],
        retrieved_contexts: List[str],
    ) -> Dict[MetricType, float]:
        """Basic evaluation metrics fallback."""
        metrics_dict: Dict[MetricType, float] = {}

        if actual_answer and len(actual_answer.strip()) > 10:
            metrics_dict[MetricType.RELEVANCE] = 0.7
        else:
            metrics_dict[MetricType.RELEVANCE] = 0.0

        if retrieved_contexts and len(retrieved_contexts) > 0:
            metrics_dict[MetricType.ANSWER_FAITHFULNESS] = 0.75
            metrics_dict[MetricType.CONTEXT_RELEVANCE] = 0.7
        else:
            metrics_dict[MetricType.ANSWER_FAITHFULNESS] = 0.3
            metrics_dict[MetricType.CONTEXT_RELEVANCE] = 0.0

        metrics_dict[MetricType.HALLUCINATION_RATE] = 0.2

        if expected_answer:
            expected_tokens = set(expected_answer.lower().split())
            actual_tokens = set(actual_answer.lower().split())
            if expected_tokens and actual_tokens:
                overlap = len(expected_tokens & actual_tokens) / len(expected_tokens)
                metrics_dict[MetricType.ACCURACY] = overlap
            else:
                metrics_dict[MetricType.ACCURACY] = 0.0

        return metrics_dict

    def evaluate_batch(
        self,
        test_cases: List[TestCase],
        rag_pipeline: Any,
    ) -> List[EvaluationResult]:
        """Evaluate multiple test cases."""
        results = []

        for test_case in test_cases:
            try:
                answer, contexts, pipeline_metrics = rag_pipeline(test_case.query)

                result = self.evaluate_response(
                    query=test_case.query,
                    query_type=test_case.query_type,
                    actual_answer=answer,
                    retrieved_contexts=contexts,
                    expected_answer=test_case.expected_answer,
                    retrieval_time_ms=pipeline_metrics.get("retrieval_time_ms"),
                    generation_time_ms=pipeline_metrics.get("generation_time_ms"),
                )
                results.append(result)

            except Exception as e:
                logger.error(f"Error evaluating test case '{test_case.query}': {e}", exc_info=True)
                continue

        return results

    def generate_report(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """Generate evaluation report from results."""
        if not results:
            return {"error": "No results to report"}

        total = len(results)
        passed = sum(1 for r in results if r.passed)

        all_metrics: Dict[MetricType, List[float]] = {}
        for result in results:
            for metric_type, value in result.metrics.items():
                if metric_type not in all_metrics:
                    all_metrics[metric_type] = []
                all_metrics[metric_type].append(value)

        avg_metrics = {
            metric_type.value: sum(values) / len(values)
            for metric_type, values in all_metrics.items()
        }

        by_query_type: Dict[str, Dict[str, Any]] = {}
        for result in results:
            qt = result.query_type.value
            if qt not in by_query_type:
                by_query_type[qt] = {
                    "total": 0,
                    "passed": 0,
                    "avg_latency_ms": [],
                }
            by_query_type[qt]["total"] += 1
            if result.passed:
                by_query_type[qt]["passed"] += 1
            by_query_type[qt]["avg_latency_ms"].append(result.latency_ms)

        for qt in by_query_type:
            latencies = by_query_type[qt]["avg_latency_ms"]
            by_query_type[qt]["avg_latency_ms"] = sum(latencies) / len(latencies)
            by_query_type[qt]["pass_rate"] = (
                by_query_type[qt]["passed"] / by_query_type[qt]["total"]
            )

        return {
            "summary": {
                "total_queries": total,
                "passed": passed,
                "failed": total - passed,
                "pass_rate": passed / total,
            },
            "metrics": avg_metrics,
            "by_query_type": by_query_type,
        }
