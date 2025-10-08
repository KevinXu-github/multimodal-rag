"""Entity and relationship extraction using LLMs."""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import json
import re


class EntityType(Enum):
    """Types of entities to extract."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    CONCEPT = "concept"
    PRODUCT = "product"
    EVENT = "event"


class RelationType(Enum):
    """Types of relationships between entities."""
    WORKS_FOR = "works_for"
    LOCATED_IN = "located_in"
    ASSOCIATED_WITH = "associated_with"
    OCCURRED_ON = "occurred_on"
    MENTIONED_IN = "mentioned_in"
    PART_OF = "part_of"
    CREATED_BY = "created_by"


@dataclass
class Entity:
    """Extracted entity."""
    name: str
    entity_type: EntityType
    confidence: float
    source_file: str
    context: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Relationship:
    """Relationship between entities."""
    source_entity: str
    target_entity: str
    relationship_type: RelationType
    confidence: float
    source_file: str
    context: Optional[str] = None


@dataclass
class ExtractionResult:
    """Result of entity/relationship extraction."""
    entities: List[Entity]
    relationships: List[Relationship]
    source_file: str
    processing_time_ms: float
