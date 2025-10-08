"""Text chunking utilities."""

from typing import List
from dataclasses import dataclass


@dataclass
class ChunkConfig:
    """Configuration for text chunking."""
    chunk_size: int = 512
    chunk_overlap: int = 50
    separator: str = "\n\n"


class TextChunker:
    """Chunks text into smaller segments."""

    def __init__(self, config: ChunkConfig = None):
        """Initialize chunker with config."""
        self.config = config or ChunkConfig()

    def chunk(self, text: str) -> List[str]:
        """Chunk text into segments."""
        if not text or len(text) <= self.config.chunk_size:
            return [text] if text else []

        chunks = []
        paragraphs = text.split(self.config.separator)

        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) <= self.config.chunk_size:
                current_chunk += para + self.config.separator
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())

                if len(para) > self.config.chunk_size:
                    para_chunks = self._chunk_long_text(para)
                    chunks.extend(para_chunks)
                    current_chunk = ""
                else:
                    current_chunk = para + self.config.separator

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _chunk_long_text(self, text: str) -> List[str]:
        """Chunk text that exceeds chunk_size."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.config.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.config.chunk_overlap

        return chunks
