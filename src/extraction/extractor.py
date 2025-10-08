"""LLM-based entity and relationship extractor."""

import time
import json
from typing import List, Dict, Any, Optional
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None
import google.generativeai as genai

from .entities import (
    Entity,
    Relationship,
    ExtractionResult,
    EntityType,
    RelationType,
)


class EntityExtractor:
    """Extracts entities and relationships using LLMs."""

    EXTRACTION_PROMPT = """Extract entities and relationships from the following text.

Return a JSON object with two keys:
1. "entities": list of entities, each with "name", "type", and "confidence" (0-1)
2. "relationships": list of relationships, each with "source", "target", "type", and "confidence"

Entity types: person, organization, location, date, concept, product, event
Relationship types: works_for, located_in, associated_with, occurred_on, mentioned_in, part_of, created_by

Text:
{text}

Return only valid JSON."""

    def __init__(
        self,
        llm_provider: str = "openai",
        model_name: str = "gpt-4",
        api_key: Optional[str] = None,
    ):
        """Initialize extractor with LLM provider."""
        self.llm_provider = llm_provider
        self.model_name = model_name

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

    def extract(
        self,
        text: str,
        source_file: str,
        max_chars: int = 4000,
    ) -> ExtractionResult:
        """Extract entities and relationships from text."""
        start_time = time.time()

        if len(text) > max_chars:
            text = text[:max_chars]

        try:
            raw_result = self._call_llm(text)
            parsed = self._parse_llm_response(raw_result)

            entities = self._create_entities(
                parsed.get("entities", []),
                source_file,
            )

            relationships = self._create_relationships(
                parsed.get("relationships", []),
                source_file,
            )

            processing_time_ms = (time.time() - start_time) * 1000

            return ExtractionResult(
                entities=entities,
                relationships=relationships,
                source_file=source_file,
                processing_time_ms=processing_time_ms,
            )

        except Exception as e:
            print(f"Extraction error: {e}")
            processing_time_ms = (time.time() - start_time) * 1000
            return ExtractionResult(
                entities=[],
                relationships=[],
                source_file=source_file,
                processing_time_ms=processing_time_ms,
            )

    def extract_batch(
        self,
        texts: List[tuple[str, str]],
    ) -> List[ExtractionResult]:
        """Extract from multiple texts."""
        results = []
        for text, source_file in texts:
            result = self.extract(text, source_file)
            results.append(result)
        return results

    def _call_llm(self, text: str) -> str:
        """Call LLM for extraction."""
        prompt = self.EXTRACTION_PROMPT.format(text=text)

        if self.llm_provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an entity extraction assistant. Return only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
            )
            return response.choices[0].message.content

        elif self.llm_provider == "anthropic":
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text

        elif self.llm_provider == "google":
            response = self.client.generate_content(prompt)
            return response.text

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response."""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(response)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {response[:200]}")
            return {"entities": [], "relationships": []}

    def _create_entities(
        self,
        entity_data: List[Dict[str, Any]],
        source_file: str,
    ) -> List[Entity]:
        """Create Entity objects from parsed data."""
        entities = []

        for data in entity_data:
            try:
                entity_type = EntityType(data["type"].lower())
                entity = Entity(
                    name=data["name"],
                    entity_type=entity_type,
                    confidence=data.get("confidence", 0.8),
                    source_file=source_file,
                )
                entities.append(entity)
            except (KeyError, ValueError) as e:
                print(f"Skipping invalid entity: {data}, error: {e}")
                continue

        return entities

    def _create_relationships(
        self,
        relationship_data: List[Dict[str, Any]],
        source_file: str,
    ) -> List[Relationship]:
        """Create Relationship objects from parsed data."""
        relationships = []

        for data in relationship_data:
            try:
                rel_type = RelationType(data["type"].lower())
                relationship = Relationship(
                    source_entity=data["source"],
                    target_entity=data["target"],
                    relationship_type=rel_type,
                    confidence=data.get("confidence", 0.8),
                    source_file=source_file,
                )
                relationships.append(relationship)
            except (KeyError, ValueError) as e:
                print(f"Skipping invalid relationship: {data}, error: {e}")
                continue

        return relationships
