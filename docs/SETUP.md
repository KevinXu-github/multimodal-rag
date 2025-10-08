# Setup Instructions

## Prerequisites

1. **Docker Desktop** (for Neo4j and Qdrant)
2. **Python 3.8+**
3. **API Keys**:
   - OpenAI API key OR Anthropic API key
4. **Tesseract OCR** (for image text extraction)
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - Mac: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

## Step-by-Step Setup

### 1. Clone Repository

```bash
cd multimodal-rag
```

### 2. Start Docker Services

**Windows:**
```bash
cd infrastructure\docker
docker-compose up -d
```

**Linux/Mac:**
```bash
cd infrastructure/docker
docker-compose up -d
```

Verify services are running:
- Neo4j: http://localhost:7474 (username: neo4j, password: password123)
- Qdrant: http://localhost:6333/dashboard

### 3. Create Virtual Environment

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Required
OPENAI_API_KEY=sk-...

# Database (defaults work if using Docker setup)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

QDRANT_HOST=localhost
QDRANT_PORT=6333

# Optional
LLM_MODEL=gpt-4
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### 6. Initialize Databases

The system will auto-initialize on first run, or manually:

```python
from src.pipeline import MultimodalRAGPipeline
import os

pipeline = MultimodalRAGPipeline(
    neo4j_uri=os.getenv("NEO4J_URI"),
    neo4j_user=os.getenv("NEO4J_USER"),
    neo4j_password=os.getenv("NEO4J_PASSWORD"),
    llm_api_key=os.getenv("OPENAI_API_KEY"),
)
pipeline.initialize()
```

### 7. Test Installation

```bash
python -m src.main
```

You should see:
```
Initializing RAG system...
RAG System Ready!
```

## Troubleshooting

### Docker Services Not Starting

```bash
# Check Docker is running
docker ps

# View logs
docker-compose logs neo4j
docker-compose logs qdrant
```

### Neo4j Connection Error

- Ensure Neo4j container is running: `docker ps`
- Check credentials in `.env` match docker-compose.yml
- Wait 10-15 seconds after `docker-compose up` for Neo4j to fully start

### Qdrant Connection Error

- Verify Qdrant is running: `curl http://localhost:6333`
- Check firewall isn't blocking port 6333

### Tesseract OCR Not Found

**Windows:**
- Install from: https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH: `C:\Program Files\Tesseract-OCR`

**Mac:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### Missing API Key

```
Error: OPENAI_API_KEY not found
```

Solution: Add API key to `.env` file

### Out of Memory

If processing large files:
- Increase Docker memory allocation (Docker Settings > Resources)
- Reduce `CHUNK_SIZE` in `.env`
- Process files individually instead of batch

## Next Steps

- [Usage Guide](./USAGE.md)
- [API Documentation](./api/)
- [Evaluation Guide](./evaluation/)
