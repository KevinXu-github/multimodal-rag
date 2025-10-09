"""Plain text document processor."""

import time
from pathlib import Path
from typing import Dict, Any, Optional
from .base import BaseProcessor, Document, ProcessingResult, Modality


class TextProcessor(BaseProcessor):
    """Processes plain text documents."""

    SUPPORTED_EXTENSIONS = {".txt", ".md", ".rst", ".log"}
    MAX_FILE_SIZE_MB = 10

    def can_process(self, file_path: Path) -> bool:
        """Check if file is a text file."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def validate(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """Validate text file."""
        if not file_path.exists():
            return False, "File does not exist"

        if not file_path.is_file():
            return False, "Path is not a file"

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            return False, f"File too large: {file_size_mb:.1f}MB > {self.MAX_FILE_SIZE_MB}MB"

        if not self.can_process(file_path):
            return False, "Not a supported text file"

        return True, None

    def process(self, file_path: Path, metadata: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """Process text file and extract content."""
        start_time = time.time()

        is_valid, error = self.validate(file_path)
        if not is_valid:
            return ProcessingResult(
                success=False,
                document=None,
                error=error,
                processing_time_ms=(time.time() - start_time) * 1000,
            )

        try:
            # Try multiple encodings
            text_content = self._read_text(file_path)

            combined_metadata = {
                "file_name": file_path.name,
                "file_size_bytes": file_path.stat().st_size,
                "encoding": "utf-8",
                **(metadata or {}),
            }

            document = Document(
                content=text_content,
                modality=Modality.TEXT,
                source_file=str(file_path),
                metadata=combined_metadata,
            )

            processing_time_ms = (time.time() - start_time) * 1000

            return ProcessingResult(
                success=True,
                document=document,
                error=None,
                processing_time_ms=processing_time_ms,
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                document=None,
                error=f"Failed to process text file: {str(e)}",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def _read_text(self, file_path: Path) -> str:
        """Read text file with encoding detection."""
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                return content.strip()
            except UnicodeDecodeError:
                continue

        # Fallback: read as binary and decode with errors='ignore'
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read().strip()
