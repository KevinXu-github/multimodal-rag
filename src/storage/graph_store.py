"""Neo4j knowledge graph storage."""

from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
import time

from ..extraction.entities import Entity, Relationship


class Neo4jGraphStore:
    """Manages knowledge graph storage in Neo4j."""

    def __init__(self, uri: str, user: str, password: str):
        """Initialize Neo4j connection."""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """Close Neo4j connection."""
        self.driver.close()

    def initialize_schema(self):
        """Create indexes and constraints."""
        with self.driver.session() as session:
            session.run(
                "CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)"
            )
            session.run(
                "CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type)"
            )
            session.run(
                "CREATE INDEX source_file IF NOT EXISTS FOR (e:Entity) ON (e.source_file)"
            )

    def add_entity(self, entity: Entity) -> bool:
        """Add or update entity in graph."""
        with self.driver.session() as session:
            try:
                session.run(
                    """
                    MERGE (e:Entity {name: $name})
                    SET e.type = $type,
                        e.confidence = $confidence,
                        e.source_file = $source_file,
                        e.context = $context,
                        e.updated_at = timestamp()
                    """,
                    name=entity.name,
                    type=entity.entity_type.value,
                    confidence=entity.confidence,
                    source_file=entity.source_file,
                    context=entity.context,
                )
                return True
            except Exception as e:
                print(f"Error adding entity: {e}")
                return False

    def add_entities_batch(self, entities: List[Entity]) -> int:
        """Add multiple entities."""
        count = 0
        with self.driver.session() as session:
            for entity in entities:
                try:
                    session.run(
                        """
                        MERGE (e:Entity {name: $name})
                        SET e.type = $type,
                            e.confidence = $confidence,
                            e.source_file = $source_file,
                            e.context = $context,
                            e.updated_at = timestamp()
                        """,
                        name=entity.name,
                        type=entity.entity_type.value,
                        confidence=entity.confidence,
                        source_file=entity.source_file,
                        context=entity.context,
                    )
                    count += 1
                except Exception as e:
                    print(f"Error adding entity {entity.name}: {e}")
        return count

    def add_relationship(self, relationship: Relationship) -> bool:
        """Add relationship between entities."""
        with self.driver.session() as session:
            try:
                session.run(
                    """
                    MATCH (source:Entity {name: $source_name})
                    MATCH (target:Entity {name: $target_name})
                    MERGE (source)-[r:RELATED {type: $rel_type}]->(target)
                    SET r.confidence = $confidence,
                        r.source_file = $source_file,
                        r.context = $context,
                        r.updated_at = timestamp()
                    """,
                    source_name=relationship.source_entity,
                    target_name=relationship.target_entity,
                    rel_type=relationship.relationship_type.value,
                    confidence=relationship.confidence,
                    source_file=relationship.source_file,
                    context=relationship.context,
                )
                return True
            except Exception as e:
                print(f"Error adding relationship: {e}")
                return False

    def add_relationships_batch(self, relationships: List[Relationship]) -> int:
        """Add multiple relationships."""
        count = 0
        with self.driver.session() as session:
            for rel in relationships:
                try:
                    session.run(
                        """
                        MATCH (source:Entity {name: $source_name})
                        MATCH (target:Entity {name: $target_name})
                        MERGE (source)-[r:RELATED {type: $rel_type}]->(target)
                        SET r.confidence = $confidence,
                            r.source_file = $source_file,
                            r.context = $context,
                            r.updated_at = timestamp()
                        """,
                        source_name=rel.source_entity,
                        target_name=rel.target_entity,
                        rel_type=rel.relationship_type.value,
                        confidence=rel.confidence,
                        source_file=rel.source_file,
                        context=rel.context,
                    )
                    count += 1
                except Exception as e:
                    print(f"Error adding relationship: {e}")
        return count

    def find_entity(self, name: str) -> Optional[Dict[str, Any]]:
        """Find entity by name."""
        with self.driver.session() as session:
            result = session.run(
                "MATCH (e:Entity {name: $name}) RETURN e",
                name=name
            )
            record = result.single()
            if record:
                return dict(record["e"])
            return None

    def find_related_entities(
        self,
        entity_name: str,
        max_hops: int = 2,
    ) -> List[Dict[str, Any]]:
        """Find entities related to given entity."""
        with self.driver.session() as session:
            # Build query dynamically to avoid parameter in relationship pattern
            query = f"""
                MATCH path = (e:Entity {{name: $name}})-[*1..{max_hops}]-(related:Entity)
                RETURN DISTINCT related, length(path) as distance
                ORDER BY distance
                """
            result = session.run(query, name=entity_name)
            return [dict(record["related"]) for record in result]

    def query_graph(
        self,
        cypher_query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute custom Cypher query."""
        with self.driver.session() as session:
            result = session.run(cypher_query, parameters or {})
            return [dict(record) for record in result]

    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        with self.driver.session() as session:
            entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()["count"]
            relationship_count = session.run("MATCH ()-[r:RELATED]->() RETURN count(r) as count").single()["count"]

            entity_types = session.run(
                """
                MATCH (e:Entity)
                RETURN e.type as type, count(*) as count
                ORDER BY count DESC
                """
            )
            type_counts = {record["type"]: record["count"] for record in entity_types}

            return {
                "total_entities": entity_count,
                "total_relationships": relationship_count,
                "entity_types": type_counts,
            }
