"""Image processor with OCR and captioning."""

import time
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
import pytesseract
from .base import BaseProcessor, Document, ProcessingResult, Modality


class ImageProcessor(BaseProcessor):
    """Processes images with OCR."""

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    MAX_FILE_SIZE_MB = 20

    def __init__(self, use_ocr: bool = True):
        """Initialize image processor."""
        self.use_ocr = use_ocr

    def can_process(self, file_path: Path) -> bool:
        """Check if file is a supported image."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def validate(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """Validate image file."""
        if not file_path.exists():
            return False, "File does not exist"

        if not file_path.is_file():
            return False, "Path is not a file"

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            return False, f"File too large: {file_size_mb:.1f}MB > {self.MAX_FILE_SIZE_MB}MB"

        if not self.can_process(file_path):
            return False, "Not a supported image format"

        try:
            with Image.open(file_path) as img:
                img.verify()
            return True, None
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"

    def process(self, file_path: Path, metadata: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """Process image and extract text via OCR."""
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
            extracted_text = ""
            image_metadata = {}

            with Image.open(file_path) as img:
                image_metadata = {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                }

                if self.use_ocr:
                    extracted_text = self._extract_text_ocr(img)

            combined_metadata = {
                "file_name": file_path.name,
                "file_size_bytes": file_path.stat().st_size,
                **image_metadata,
                **(metadata or {}),
            }

            document = Document(
                content=extracted_text or f"[Image: {file_path.name}]",
                modality=Modality.IMAGE,
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
                error=f"Failed to process image: {str(e)}",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def _extract_text_ocr(self, image: Image.Image) -> str:
        """Extract text from image using OCR."""
        try:
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"OCR failed: {e}")
            return ""
