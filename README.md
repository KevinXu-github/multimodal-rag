# Multimodal Enterprise RAG System

Enterprise-grade Retrieval-Augmented Generation system with multimodal support (text, image, audio) and hybrid knowledge retrieval combining knowledge graphs and vector search.

## Features

- **Multimodal Ingestion**: Process PDF, images (with OCR), and audio (with transcription)
- **Knowledge Graph**: Entity and relationship extraction stored in Neo4j
- **Vector Search**: Semantic search using Qdrant
- **Hybrid Retrieval**: Combines graph traversal, keyword filtering, and vector search
- **LLM Integration**: Support for OpenAI and Anthropic models
- **Evaluation Framework**: Built-in evaluation with DeepEval
- **Web UI**: Streamlit interface for easy interaction

## Architecture

```
multimodal-rag/
├── src/
│   ├── ingestion/      # Multimodal document processing
│   ├── extraction/     # Entity/relationship extraction
│   ├── storage/        # Neo4j and Qdrant integration
│   ├── retrieval/      # Hybrid search engine
│   ├── generation/     # Answer generation
│   ├── evaluation/     # Evaluation framework
│   └── ui/             # Streamlit web interface
├── infrastructure/     # Docker configuration
├── tests/              # Test suite
└── docs/               # Documentation
```

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose
- Python 3.8+
- OpenAI or Anthropic API key

### 2. Setup Infrastructure

Start Neo4j and Qdrant:

```bash
# On Windows
scripts\setup\setup_docker.bat

# On Linux/Mac
bash scripts/setup/setup_docker.sh
```

### 3. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=your_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_PASSWORD=password123
QDRANT_HOST=localhost
```

### 5. Run the System

**CLI Mode:**
```bash
python -m src.main
```

**Web UI:**
```bash
streamlit run src/ui/app.py
```

## Usage

### CLI Commands

```bash
> ingest /path/to/file.pdf          # Ingest single file
> ingest /path/to/directory         # Ingest directory
> query What is mentioned about X?  # Ask question
> stats                             # Show statistics
> exit                              # Quit
```

### Web UI

1. Navigate to http://localhost:8501
2. Use the "Upload" tab to add documents
3. Use the "Query" tab to ask questions
4. View system statistics in the "Statistics" tab

## Evaluation

The system includes an evaluation-first framework with:

- Query types: Factual, Lookup, Summarization, Semantic Linkage, Reasoning
- Metrics: Accuracy, Relevance, Hallucination Rate, Latency
- DeepEval integration for comprehensive testing

## Supported File Types

- **Text**: PDF, TXT
- **Images**: JPG, PNG (with OCR)
- **Audio**: MP3, WAV (with Whisper transcription)

## Development

### Run Tests

```bash
pytest tests/
```

### Format Code

```bash
black src/ tests/
isort src/ tests/
```

### Lint

```bash
flake8 src/
mypy src/
```

## System Requirements

- RAM: 8GB minimum, 16GB recommended
- Storage: Depends on dataset size
- GPU: Optional, improves Whisper transcription speed

## Services

- **Neo4j Browser**: http://localhost:7474
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Streamlit UI**: http://localhost:8501

## License

See LICENSE file

## Author

Kevin Xu (xuk654@gmail.com)
