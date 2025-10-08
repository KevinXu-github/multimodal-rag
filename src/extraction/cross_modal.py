"""Cross-modal entity linking."""

from typing import List, Dict, Set
from difflib import SequenceMatcher

from .entities import Entity, Relationship, RelationType


class CrossModalLinker:
    """Links entities across different modalities."""

    def __init__(self, similarity_threshold: float = 0.85):
        """Initialize linker with similarity threshold."""
        self.similarity_threshold = similarity_threshold

    def link_entities(
        self,
        entities: List[Entity],
    ) -> Dict[str, List[Entity]]:
        """Link similar entities across modalities."""
        entity_groups: Dict[str, List[Entity]] = {}

        for entity in entities:
            matched = False

            for canonical_name, group in entity_groups.items():
                if self._are_similar(entity.name, canonical_name):
                    group.append(entity)
                    matched = True
                    break

            if not matched:
                entity_groups[entity.name] = [entity]

        return entity_groups

    def create_cross_modal_relationships(
        self,
        entity_groups: Dict[str, List[Entity]],
    ) -> List[Relationship]:
        """Create relationships for entities appearing in multiple sources."""
        relationships = []

        for canonical_name, entities in entity_groups.items():
            if len(entities) < 2:
                continue

            sources = set(e.source_file for e in entities)
            if len(sources) < 2:
                continue

            for i, entity1 in enumerate(entities):
                for entity2 in entities[i + 1:]:
                    if entity1.source_file != entity2.source_file:
                        relationships.append(
                            Relationship(
                                source_entity=entity1.name,
                                target_entity=entity2.name,
                                relationship_type=RelationType.MENTIONED_IN,
                                confidence=0.9,
                                source_file="cross_modal_linking",
                                context=f"Same entity across {entity1.modality} and {entity2.modality}",
                            )
                        )

        return relationships

    def _are_similar(self, name1: str, name2: str) -> bool:
        """Check if two entity names are similar."""
        similarity = SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
        return similarity >= self.similarity_threshold
