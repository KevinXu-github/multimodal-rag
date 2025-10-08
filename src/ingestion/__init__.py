"""Ingestion module for multimodal document processing."""

from .base import BaseProcessor, Document, ProcessingResult, Modality
from .pdf_processor import PDFProcessor
from .image_processor import ImageProcessor
from .audio_processor import AudioProcessor
from .chunker import TextChunker, ChunkConfig
from .pipeline import IngestionPipeline

__all__ = [
    "BaseProcessor",
    "Document",
    "ProcessingResult",
    "Modality",
    "PDFProcessor",
    "ImageProcessor",
    "AudioProcessor",
    "TextChunker",
    "ChunkConfig",
    "IngestionPipeline",
]
