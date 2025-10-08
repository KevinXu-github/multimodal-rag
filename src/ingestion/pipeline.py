"""Ingestion pipeline orchestration."""

import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import BaseProcessor, Document, ProcessingResult
from .pdf_processor import PDFProcessor
from .image_processor import ImageProcessor
from .audio_processor import AudioProcessor
from .chunker import TextChunker, ChunkConfig


class IngestionPipeline:
    """Orchestrates multimodal document ingestion."""

    def __init__(
        self,
        chunk_config: Optional[ChunkConfig] = None,
        max_workers: int = 4,
        whisper_model: str = "base",
    ):
        """Initialize ingestion pipeline."""
        self.processors: List[BaseProcessor] = [
            PDFProcessor(),
            ImageProcessor(use_ocr=True),
            AudioProcessor(model_name=whisper_model),
        ]
        self.chunker = TextChunker(chunk_config or ChunkConfig())
        self.max_workers = max_workers

    def process_file(
        self,
        file_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
        enable_chunking: bool = True,
    ) -> ProcessingResult:
        """Process a single file."""
        processor = self._get_processor(file_path)

        if not processor:
            return ProcessingResult(
                success=False,
                document=None,
                error=f"No processor available for {file_path.suffix}",
                processing_time_ms=0,
            )

        result = processor.process(file_path, metadata)

        if result.success and enable_chunking and result.document:
            result.document.chunks = self.chunker.chunk(result.document.content)

        return result

    def process_directory(
        self,
        directory: Path,
        recursive: bool = True,
        enable_chunking: bool = True,
    ) -> List[ProcessingResult]:
        """Process all supported files in a directory."""
        files = self._get_files(directory, recursive)

        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.process_file, f, None, enable_chunking): f
                for f in files
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    file_path = futures[future]
                    results.append(
                        ProcessingResult(
                            success=False,
                            document=None,
                            error=f"Exception processing {file_path}: {str(e)}",
                            processing_time_ms=0,
                        )
                    )

        return results

    def process_batch(
        self,
        file_paths: List[Path],
        enable_chunking: bool = True,
    ) -> List[ProcessingResult]:
        """Process multiple files in parallel."""
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.process_file, f, None, enable_chunking): f
                for f in file_paths
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    file_path = futures[future]
                    results.append(
                        ProcessingResult(
                            success=False,
                            document=None,
                            error=f"Exception: {str(e)}",
                            processing_time_ms=0,
                        )
                    )

        return results

    def _get_processor(self, file_path: Path) -> Optional[BaseProcessor]:
        """Get appropriate processor for file."""
        for processor in self.processors:
            if processor.can_process(file_path):
                return processor
        return None

    def _get_files(self, directory: Path, recursive: bool) -> List[Path]:
        """Get all processable files from directory."""
        files = []

        if recursive:
            for processor in self.processors:
                for ext in getattr(processor, "SUPPORTED_EXTENSIONS", []):
                    files.extend(directory.rglob(f"*{ext}"))
        else:
            for processor in self.processors:
                for ext in getattr(processor, "SUPPORTED_EXTENSIONS", []):
                    files.extend(directory.glob(f"*{ext}"))

        return files

    def get_stats(self, results: List[ProcessingResult]) -> Dict[str, Any]:
        """Generate statistics from processing results."""
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful

        total_time_ms = sum(r.processing_time_ms for r in results)
        avg_time_ms = total_time_ms / total if total > 0 else 0

        modality_counts = {}
        for result in results:
            if result.success and result.document:
                modality = result.document.modality.value
                modality_counts[modality] = modality_counts.get(modality, 0) + 1

        return {
            "total_files": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "total_time_ms": total_time_ms,
            "avg_time_ms": avg_time_ms,
            "by_modality": modality_counts,
        }
