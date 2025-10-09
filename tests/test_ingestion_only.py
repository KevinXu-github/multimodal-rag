"""Test ingestion pipeline without databases."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion import IngestionPipeline

print("=" * 60)
print("Testing Ingestion Pipeline (No Database Required)")
print("=" * 60)

# Initialize ingestion pipeline
print("\n1. Initializing ingestion pipeline...")
pipeline = IngestionPipeline()
print("[OK] Pipeline created")

# Test with the challenge PDF
print("\n2. Testing PDF processing...")
pdf_file = Path(__file__).parent.parent / "HybridMultiModalChallenge.pdf"

if pdf_file.exists():
    print(f"Found: {pdf_file}")
    result = pipeline.process_file(pdf_file)

    if result.success:
        print(f"[OK] Successfully processed PDF")
        print(f"  - Processing time: {result.processing_time_ms:.0f}ms")
        print(f"  - Content length: {len(result.document.content)} chars")
        print(f"  - Chunks created: {len(result.document.chunks) if result.document.chunks else 0}")
        print(f"  - Metadata: {result.document.metadata}")
        print(f"\nFirst 200 characters:")
        print(result.document.content[:200])
    else:
        print(f"[FAILED] {result.error}")
else:
    print(f"[ERROR] File not found: {pdf_file}")
    print("\nYou can test with any PDF file:")
    print("  pdf_file = Path('your_file.pdf')")

print("\n" + "=" * 60)
print("Ingestion test complete!")
print("\nThis test shows the ingestion works without databases.")
print("Once Docker is running, you can test the full pipeline.")
print("=" * 60)
