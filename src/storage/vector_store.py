"""Qdrant vector storage."""

import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """Manages vector storage in Qdrant."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "documents",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        """Initialize Qdrant connection."""
        self.client = QdrantClient(host=host, port=port, timeout=60, check_compatibility=False)
        self.collection_name = collection_name
        self.embedding_model = SentenceTransformer(embedding_model)
        self.vector_size = self.embedding_model.get_sentence_embedding_dimension()

    def initialize_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )

    def add_document(
        self,
        doc_id: str,
        text: str,
        metadata: Dict[str, Any],
    ) -> bool:
        """Add single document to vector store."""
        try:
            embedding = self.embedding_model.encode(text).tolist()

            point = PointStruct(
                id=doc_id,
                vector=embedding,
                payload={
                    "text": text,
                    **metadata,
                },
            )

            self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
            )
            return True

        except Exception as e:
            logger.error(f"Error adding document: {e}", exc_info=True)
            return False

    def add_documents_batch(
        self,
        documents: List[tuple[str, str, Dict[str, Any]]],
    ) -> int:
        """Add multiple documents."""
        count = 0
        points = []

        try:
            texts = [doc[1] for doc in documents]
            embeddings = self.embedding_model.encode(texts)

            for i, ((doc_id, text, metadata), embedding) in enumerate(zip(documents, embeddings)):
                # Use incremental integer IDs instead of strings
                point = PointStruct(
                    id=i,
                    vector=embedding.tolist(),
                    payload={
                        "doc_id": str(doc_id),
                        "text": text,
                        **metadata,
                    },
                )
                points.append(point)

            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
            count = len(points)

        except Exception as e:
            logger.error(f"Error adding documents batch: {e}", exc_info=True)

        return count

    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Semantic search for similar documents."""
        try:
            query_embedding = self.embedding_model.encode(query).tolist()

            search_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value),
                        )
                    )
                if conditions:
                    search_filter = Filter(must=conditions)

            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=search_filter,
            )

            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "text": hit.payload.get("text", ""),
                    "metadata": {k: v for k, v in hit.payload.items() if k != "text"},
                }
                for hit in results
            ]

        except Exception as e:
            logger.error(f"Error searching: {e}", exc_info=True)
            return []

    def delete_by_source(self, source_file: str) -> bool:
        """Delete all documents from a source file."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="source_file",
                            match=MatchValue(value=source_file),
                        )
                    ]
                ),
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting documents: {e}", exc_info=True)
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "total_vectors": collection_info.points_count,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance.name,
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            return {}
