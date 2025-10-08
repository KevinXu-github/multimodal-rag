"""Answer generation using LLMs."""

import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None
import google.generativeai as genai

from ..retrieval.hybrid_search import SearchResult


@dataclass
class GeneratedAnswer:
    """Generated answer with metadata."""
    answer: str
    contexts_used: List[str]
    confidence: float
    generation_time_ms: float
    model_used: str


class AnswerGenerator:
    """Generates answers from retrieved context."""

    SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on provided context.

Rules:
1. Only use information from the provided context
2. If the context doesn't contain the answer, say so
3. Cite sources when possible
4. Be concise and accurate
5. Do not hallucinate or make up information"""

    ANSWER_PROMPT = """Context:
{context}

Question: {question}

Answer the question based only on the context provided above. If the context doesn't contain enough information, say "I don't have enough information to answer this question."""

    def __init__(
        self,
        llm_provider: str = "openai",
        model_name: str = "gpt-4",
        api_key: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 500,
    ):
        """Initialize generator."""
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        if llm_provider == "openai":
            if OpenAI is None:
                raise ImportError("OpenAI not installed. Install with: pip install openai")
            self.client = OpenAI(api_key=api_key)
        elif llm_provider == "anthropic":
            if Anthropic is None:
                raise ImportError("Anthropic not installed. Install with: pip install anthropic")
            self.client = Anthropic(api_key=api_key)
        elif llm_provider == "google":
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(model_name)
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")

    def generate(
        self,
        question: str,
        search_results: List[SearchResult],
        max_context_length: int = 3000,
    ) -> GeneratedAnswer:
        """Generate answer from search results."""
        start_time = time.time()

        context = self._prepare_context(search_results, max_context_length)
        contexts_used = [r.content for r in search_results[:5]]

        try:
            answer = self._call_llm(question, context)
            confidence = self._estimate_confidence(answer, context)

            generation_time_ms = (time.time() - start_time) * 1000

            return GeneratedAnswer(
                answer=answer,
                contexts_used=contexts_used,
                confidence=confidence,
                generation_time_ms=generation_time_ms,
                model_used=self.model_name,
            )

        except Exception as e:
            print(f"Generation error: {e}")
            generation_time_ms = (time.time() - start_time) * 1000

            return GeneratedAnswer(
                answer=f"Error generating answer: {str(e)}",
                contexts_used=contexts_used,
                confidence=0.0,
                generation_time_ms=generation_time_ms,
                model_used=self.model_name,
            )

    def _prepare_context(
        self,
        results: List[SearchResult],
        max_length: int,
    ) -> str:
        """Prepare context from search results."""
        context_parts = []
        current_length = 0

        for i, result in enumerate(results, 1):
            source = result.metadata.get("file_name", result.source)
            part = f"[Source {i}: {source}]\n{result.content}\n"

            if current_length + len(part) > max_length:
                break

            context_parts.append(part)
            current_length += len(part)

        return "\n".join(context_parts)

    def _call_llm(self, question: str, context: str) -> str:
        """Call LLM to generate answer."""
        prompt = self.ANSWER_PROMPT.format(
            context=context,
            question=question,
        )

        if self.llm_provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content

        elif self.llm_provider == "anthropic":
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                system=self.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text

        elif self.llm_provider == "google":
            full_prompt = f"{self.SYSTEM_PROMPT}\n\n{prompt}"
            response = self.client.generate_content(full_prompt)
            return response.text

    def _estimate_confidence(self, answer: str, context: str) -> float:
        """Estimate confidence in generated answer."""
        if "don't have enough information" in answer.lower():
            return 0.3

        if "i don't know" in answer.lower():
            return 0.2

        if len(answer) < 20:
            return 0.5

        return 0.8
