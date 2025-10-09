"""Audio processor with transcription."""

import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
from .base import BaseProcessor, Document, ProcessingResult, Modality

logger = logging.getLogger(__name__)


class AudioProcessor(BaseProcessor):
    """Processes audio files with transcription."""

    SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}
    MAX_FILE_SIZE_MB = 100

    def __init__(self, model_name: str = "base"):
        """Initialize audio processor with Whisper model."""
        if not WHISPER_AVAILABLE:
            logger.warning("Warning: Whisper not installed. Audio processing will fail.")
            logger.info("Install with: pip install openai-whisper")
        self.model_name = model_name
        self._model = None

    def can_process(self, file_path: Path) -> bool:
        """Check if file is a supported audio format."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def validate(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """Validate audio file."""
        if not file_path.exists():
            return False, "File does not exist"

        if not file_path.is_file():
            return False, "Path is not a file"

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            return False, f"File too large: {file_size_mb:.1f}MB > {self.MAX_FILE_SIZE_MB}MB"

        if not self.can_process(file_path):
            return False, "Not a supported audio format"

        return True, None

    def process(self, file_path: Path, metadata: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """Process audio and transcribe to text."""
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
            if self._model is None:
                self._model = whisper.load_model(self.model_name)

            result = self._model.transcribe(str(file_path))
            transcript = result["text"]
            language = result.get("language", "unknown")

            combined_metadata = {
                "file_name": file_path.name,
                "file_size_bytes": file_path.stat().st_size,
                "language": language,
                "transcription_model": self.model_name,
                **(metadata or {}),
            }

            document = Document(
                content=transcript,
                modality=Modality.AUDIO,
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
                error=f"Failed to process audio: {str(e)}",
                processing_time_ms=(time.time() - start_time) * 1000,
            )
