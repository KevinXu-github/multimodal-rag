"""PDF document processor."""

import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import pypdf
from .base import BaseProcessor, Document, ProcessingResult, Modality


class PDFProcessor(BaseProcessor):
    """Processes PDF documents."""

    SUPPORTED_EXTENSIONS = {".pdf"}
    MAX_FILE_SIZE_MB = 50

    def can_process(self, file_path: Path) -> bool:
        """Check if file is a PDF."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def validate(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """Validate PDF file."""
        if not file_path.exists():
            return False, "File does not exist"

        if not file_path.is_file():
            return False, "Path is not a file"

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            return False, f"File too large: {file_size_mb:.1f}MB > {self.MAX_FILE_SIZE_MB}MB"

        if not self.can_process(file_path):
            return False, "Not a PDF file"

        return True, None

    def process(self, file_path: Path, metadata: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """Process PDF and extract text."""
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
            text_content = self._extract_text(file_path)
            pdf_metadata = self._extract_metadata(file_path)

            combined_metadata = {
                "file_name": file_path.name,
                "file_size_bytes": file_path.stat().st_size,
                "page_count": pdf_metadata.get("page_count", 0),
                **pdf_metadata,
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
                error=f"Failed to process PDF: {str(e)}",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def _extract_text(self, file_path: Path) -> str:
        """Extract text from PDF."""
        text_parts = []

        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)

            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text.strip():
                    text_parts.append(f"[Page {page_num}]\n{page_text}")

        return "\n\n".join(text_parts)

    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from PDF."""
        metadata = {}

        try:
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                metadata["page_count"] = len(reader.pages)

                if reader.metadata:
                    pdf_meta = reader.metadata
                    metadata["title"] = pdf_meta.get("/Title", "")
                    metadata["author"] = pdf_meta.get("/Author", "")
                    metadata["subject"] = pdf_meta.get("/Subject", "")
                    metadata["creator"] = pdf_meta.get("/Creator", "")

        except Exception as e:
            print(f"Warning: Could not extract PDF metadata: {e}")

        return metadata
