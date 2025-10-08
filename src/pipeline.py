"""Main RAG pipeline orchestrating all components."""

import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .ingestion import IngestionPipeline, Document, ChunkConfig
from .extraction import EntityExtractor, CrossModalLinker
from .storage import Neo4jGraphStore, QdrantVectorStore
from .retrieval import HybridSearchEngine, QueryProcessor
from .generation import AnswerGenerator
from .evaluation import RAGEvaluator, GracefulFailureHandler


@dataclass
class RAGResponse:
    """Complete RAG system response."""
    question: str
    answer: str
    contexts: List[str]
    confidence: float
    metrics: Dict[str, float]


class MultimodalRAGPipeline:
    """Main pipeline for the multimodal RAG system."""

    def __init__(
        self,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        llm_provider: str = "google",
        llm_model: str = "gemini-1.5-flash",
        llm_api_key: Optional[str] = None,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        enable_evaluation: bool = True,
    ):
        """Initialize RAG pipeline."""
        self.graph_store = Neo4jGraphStore(neo4j_uri, neo4j_user, neo4j_password)
        self.vector_store = QdrantVectorStore(
            host=qdrant_host,
            port=qdrant_port,
            embedding_model=embedding_model,
        )

        self.ingestion = IngestionPipeline()
        self.extractor = EntityExtractor(
            llm_provider=llm_provider,
            model_name=llm_model,
            api_key=llm_api_key,
        )
        self.linker = CrossModalLinker()

        self.search_engine = HybridSearchEngine(
            graph_store=self.graph_store,
            vector_store=self.vector_store,
        )

        self.query_processor = QueryProcessor()
        self.generator = AnswerGenerator(
            llm_provider=llm_provider,
            model_name=llm_model,
            api_key=llm_api_key,
        )

        self.evaluator = RAGEvaluator() if enable_evaluation else None
        self.failure_handler = GracefulFailureHandler()

    def initialize(self):
        """Initialize databases and schemas."""
        self.graph_store.initialize_schema()
        self.vector_store.initialize_collection()

    def ingest_file(self, file_path: Path) -> bool:
        """Ingest a single file into the system."""
        try:
            result = self.ingestion.process_file(file_path)

            if not result.success:
                print(f"Failed to process {file_path}: {result.error}")
                return False

            doc = result.document
            self._store_document(doc)
            self._extract_and_store_entities(doc)

            return True

        except Exception as e:
            print(f"Error ingesting {file_path}: {e}")
            return False

    def ingest_directory(self, directory: Path) -> Dict[str, Any]:
        """Ingest all files in a directory."""
        results = self.ingestion.process_directory(directory)

        successful = 0
        failed = 0

        for result in results:
            if result.success:
                self._store_document(result.document)
                self._extract_and_store_entities(result.document)
                successful += 1
            else:
                failed += 1

        return {
            "total": len(results),
            "successful": successful,
            "failed": failed,
        }

    def query(self, question: str) -> RAGResponse:
        """Answer a question using the RAG system."""
        start_time = time.time()

        processed = self.query_processor.process(question)

        if not processed.is_valid:
            return RAGResponse(
                question=question,
                answer=self.failure_handler.validation_error(
                    processed.validation_error
                ),
                contexts=[],
                confidence=0.0,
                metrics={"total_time_ms": (time.time() - start_time) * 1000},
            )

        try:
            search_result = self.search_engine.search(
                query=processed.processed_query,
                top_k=5,
            )

            if not search_result.results:
                return RAGResponse(
                    question=question,
                    answer=self.failure_handler.no_context_found(),
                    contexts=[],
                    confidence=0.0,
                    metrics={
                        "retrieval_time_ms": search_result.retrieval_time_ms,
                        "total_time_ms": (time.time() - start_time) * 1000,
                    },
                )

            generated = self.generator.generate(
                question=question,
                search_results=search_result.results,
            )

            total_time_ms = (time.time() - start_time) * 1000

            return RAGResponse(
                question=question,
                answer=generated.answer,
                contexts=generated.contexts_used,
                confidence=generated.confidence,
                metrics={
                    "retrieval_time_ms": search_result.retrieval_time_ms,
                    "generation_time_ms": generated.generation_time_ms,
                    "total_time_ms": total_time_ms,
                },
            )

        except Exception as e:
            print(f"Query error: {e}")
            return RAGResponse(
                question=question,
                answer=f"An error occurred: {str(e)}",
                contexts=[],
                confidence=0.0,
                metrics={"total_time_ms": (time.time() - start_time) * 1000},
            )

    def _store_document(self, doc: Document):
        """Store document in vector database."""
        if doc.chunks:
            documents = [
                (
                    f"{doc.source_file}_{i}",
                    chunk,
                    {
                        "source_file": doc.source_file,
                        "modality": doc.modality.value,
                        "chunk_index": i,
                        **doc.metadata,
                    },
                )
                for i, chunk in enumerate(doc.chunks)
            ]
            self.vector_store.add_documents_batch(documents)

    def _extract_and_store_entities(self, doc: Document):
        """Extract entities and store in graph."""
        extraction_result = self.extractor.extract(
            text=doc.content,
            source_file=doc.source_file,
        )

        if extraction_result.entities:
            self.graph_store.add_entities_batch(extraction_result.entities)

        if extraction_result.relationships:
            self.graph_store.add_relationships_batch(extraction_result.relationships)

    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        return {
            "graph": self.graph_store.get_stats(),
            "vector": self.vector_store.get_stats(),
        }

    def close(self):
        """Close all connections."""
        self.graph_store.close()
