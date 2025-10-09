# Multimodal Enterprise RAG System

**72-Hour Technical Challenge Submission** - Enterprise-grade Retrieval-Augmented Generation system with multimodal support and hybrid knowledge retrieval combining knowledge graphs and vector search.

## Challenge Requirements Met

- **Evaluation-first approach** with DeepEval integration
- **3+ modalities**: PDF, Images (OCR), Audio (Whisper transcription)
- **Knowledge Graph**: Neo4j with entity/relationship extraction
- **Vector Database**: Qdrant with semantic search
- **Hybrid Search**: Graph traversal + Keyword filtering + Vector retrieval
- **LLM-based extraction** with cross-modal entity linking
- **User Interface**: CLI + Streamlit web UI
- **Production-ready**: Docker deployment, comprehensive docs, testing

## Features

- **Multimodal Ingestion Pipeline**: Process PDF, images (Tesseract/EasyOCR), and audio (OpenAI Whisper)
- **Knowledge Graph (Neo4j)**: LLM-based entity and relationship extraction (7 entity types, 7 relationship types)
- **Vector Database (Qdrant)**: Semantic search with Sentence Transformers embeddings
- **Agent-Based Retrieval**: Specialized agents (Factual, Lookup, Reasoning) with query-type routing
- **Hybrid Search Engine**: Combines graph traversal (30%), keyword filtering (20%), and vector retrieval (50%)
- **LLM Integration**: Ollama (default), Google Gemini, OpenAI, and Anthropic models
- **Evaluation Framework**: 5 query types, 8 metrics, DeepEval integration with graceful failures
- **Dual Interface**: CLI and Streamlit web UI

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

- Docker Desktop (for Neo4j + Qdrant)
- Python 3.8+
- Ollama - [Download](https://ollama.com/download)

### 2. Start Infrastructure

**Start Neo4j and Qdrant with Docker:**

```bash
# Navigate to docker directory
cd infrastructure/docker

# Start services
docker-compose up -d

# Verify services are running
# Neo4j Browser: http://localhost:7474 (neo4j/password123)
# Qdrant Dashboard: http://localhost:6333/dashboard
```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# Mac/Linux:
source venv/bin/activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Ollama

Download and install from [ollama.com/download](https://ollama.com/download)

Pull the llama3.2 model:
```bash
ollama pull llama3.2
```

### 5. Configure Environment

```bash
cp .env.example .env
```

Required in `.env`:
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_PASSWORD=password123
QDRANT_HOST=localhost

# Optional: To use other LLM providers
# LLM_PROVIDER=google
# LLM_MODEL=gemini-1.5-flash
# GOOGLE_API_KEY=your_api_key_here
```

### 6. Run the System

**CLI:**
```bash
python main.py
```

**Web UI:**
```bash
streamlit run src/ui/app.py
# Opens http://localhost:8501
```

**Test:**
```bash
python -m pytest tests/
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

## Evaluation Framework

Built with **evaluation-first mindset** as required by the challenge:

**Query Types (5):**
- Factual: Direct fact retrieval
- Lookup: Entity/attribute search
- Summarization: Multi-document synthesis
- Semantic Linkage: Cross-modal relationships
- Reasoning: Multi-hop inference

**Metrics Tracked (8):**
- Accuracy, Relevance, Context Precision
- Hallucination Rate, Answer Faithfulness
- Context Relevance, Context Recall
- Latency (retrieval + generation)

**Tools:**
- DeepEval integration with fallback metrics
- Graceful failure handling (5 scenarios)
- Per-query-type evaluation reports

## Supported File Types

**3 Modalities Implemented:**
- **Text Documents**: PDF, TXT (PyPDF extraction)
- **Images**: JPG, PNG (Tesseract + EasyOCR for text extraction)
- **Audio**: MP3, WAV (OpenAI Whisper transcription)

**Processing Features:**
- Parallel batch ingestion
- Metadata extraction
- Semantic chunking (configurable size/overlap)
- Cross-modal entity linking

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

## Architecture Highlights

```
Query Flow:
User Query → Query Processor (validation)
          → Hybrid Search (Graph + Vector + Keyword)
          → Score Merging & Reranking
          → Answer Generation (LLM)
          → Evaluation & Metrics

Ingestion Flow:
File Upload → Modality Detection → Content Extraction
           → Entity Extraction (LLM) → Dual Storage (Neo4j + Qdrant)
```

**Key Design Decisions:**
- **Hybrid retrieval** with weighted score merging (Graph 30%, Vector 50%, Keyword 20%)
- **Cross-modal linking** to connect entities across different file types
- **Graceful degradation** with fallback mechanisms
- **Modular architecture** for easy extension

## System Requirements

- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: ~5GB (Docker images + embeddings model)
- **GPU**: Optional, speeds up Whisper transcription
- **OS**: Windows, macOS, or Linux

## Service Endpoints

- **Neo4j Browser**: http://localhost:7474 (neo4j/password123)
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Streamlit UI**: http://localhost:8501

## Documentation

- `QUICKSTART.md` - Step-by-step setup guide
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation details
- `SYSTEM_READY.md` - System status and testing guide
- `docs/` - Comprehensive architecture documentation

## Challenge Submission

**Aparavi 72-Hour Technical Challenge**
Multimodal Enterprise RAG with Knowledge Graphs and Hybrid Search

**Author**: Kevin Xu
**Email**: xuk654@gmail.com
**GitHub**: https://github.com/KevinXu-github/multimodal-rag

## License

See LICENSE file
