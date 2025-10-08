# Evaluation Framework

## Overview

This RAG system follows an evaluation-first approach as required by enterprise best practices.

## Success Criteria

### Query Types Supported

1. **Factual**: Direct fact retrieval from documents
2. **Lookup**: Entity and relationship lookups
3. **Summarization**: Multi-document summarization
4. **Semantic Linkage**: Cross-modal entity connections
5. **Reasoning**: Multi-hop reasoning over knowledge graph

### Evaluation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Accuracy | Correctness of response | > 0.8 |
| Relevance | Answer relevancy to query | > 0.75 |
| Hallucination Rate | Ungrounded claims | < 0.1 |
| Latency | Response time | < 5s |
| Retrieval Precision | Relevant docs retrieved | > 0.7 |
| Context Relevance | Retrieved context quality | > 0.8 |
| Answer Faithfulness | Groundedness in context | > 0.85 |

### Per Query Type Targets

**Factual Queries**:
- Accuracy: > 0.9
- Latency: < 3s
- Hallucination: < 0.05

**Lookup Queries**:
- Accuracy: > 0.85
- Latency: < 2s

**Summarization**:
- Accuracy: > 0.75
- Latency: < 8s
- Hallucination: < 0.15

**Semantic Linkage**:
- Accuracy: > 0.8
- Latency: < 6s

**Reasoning**:
- Accuracy: > 0.75
- Latency: < 10s

## Graceful Failure Handling

The system handles failures gracefully in these scenarios:

- No relevant context found
- Out of domain queries
- Multimodal processing errors
- Service unavailability
- Input validation failures

All failures return informative messages without exposing system internals.

## Usage

```python
from src.evaluation import RAGEvaluator, TestCase, QueryType

evaluator = RAGEvaluator()

result = evaluator.evaluate_response(
    query="What is X?",
    query_type=QueryType.FACTUAL,
    actual_answer="X is...",
    retrieved_contexts=["context1", "context2"],
)

print(f"Passed: {result.passed}")
print(f"Metrics: {result.metrics}")
```
