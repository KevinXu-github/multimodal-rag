"""Base classes for ingestion pipeline."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
from pathlib import Path


class Modality(Enum):
    """Supported modalities."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


@dataclass
class Document:
    """Processed document with metadata."""
    content: str
    modality: Modality
    source_file: str
    metadata: Dict[str, Any]
    chunks: Optional[List[str]] = None
    embeddings: Optional[List[List[float]]] = None


@dataclass
class ProcessingResult:
    """Result of processing a file."""
    success: bool
    document: Optional[Document]
    error: Optional[str]
    processing_time_ms: float


class BaseProcessor(ABC):
    """Base processor for all modalities."""

    @abstractmethod
    def can_process(self, file_path: Path) -> bool:
        """Check if this processor can handle the file."""
        pass

    @abstractmethod
    def process(self, file_path: Path, metadata: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """Process the file and extract content."""
        pass

    @abstractmethod
    def validate(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """Validate file before processing."""
        pass
