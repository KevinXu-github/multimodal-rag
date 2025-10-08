# Quick Start Guide

## Prerequisites Check

Before starting, ensure you have:
- [ ] Docker Desktop installed and running
- [ ] Python 3.8+ installed
- [ ] OpenAI API key

## Step-by-Step Setup

### 1. Start Docker Services

Open a terminal in the project directory:

```bash
cd infrastructure/docker
docker-compose up -d
```

Wait 10-15 seconds for services to start, then verify:
- Neo4j: Open http://localhost:7474 (username: `neo4j`, password: `password123`)
- Qdrant: Open http://localhost:6333/dashboard

### 2. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will take a few minutes.

### 4. Configure API Key

Create `.env` file:

```bash
# Copy example
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-key-here
```

### 5. Test the System

Run the test script:

```bash
python test_system.py
```

Expected output:
```
============================================================
Multimodal RAG System Test
============================================================

1. Checking configuration...
✓ API key found

2. Initializing pipeline...
✓ Pipeline created

3. Initializing databases...
✓ Databases initialized

...
```

### 6. Run the Application

**Option A: Web UI (Recommended for first-time users)**

```bash
streamlit run src/ui/app.py
```

Opens http://localhost:8501

**Option B: CLI**

```bash
python -m src.main
```

Commands:
- `ingest <file>` - Upload a file
- `query <question>` - Ask a question
- `stats` - View statistics
- `exit` - Quit

## Quick Demo

### Upload a Document

**Web UI:**
1. Go to "Upload" tab
2. Choose a PDF file
3. Click "Process File"

**CLI:**
```bash
> ingest HybridMultiModalChallenge.pdf
```

### Ask Questions

**Web UI:**
1. Go to "Query" tab
2. Type: "What are the main requirements?"
3. Click "Search"

**CLI:**
```bash
> query What are the main requirements?
```

## Troubleshooting

### Docker not running
```bash
# Check if containers are running
docker ps

# Should see neo4j and qdrant containers
```

### Connection errors
```bash
# Restart containers
cd infrastructure/docker
docker-compose down
docker-compose up -d
```

### Missing API key
```bash
# Check .env file exists and has key
cat .env
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## What to Test

1. **PDF Upload**: Test with the challenge PDF or any PDF document
2. **Image Upload**: Test with a JPG/PNG image containing text
3. **Audio Upload**: Test with MP3/WAV audio file
4. **Queries**:
   - Factual: "What is X?"
   - Lookup: "Find mentions of Y"
   - Summary: "Summarize the document"
   - Cross-modal: "What appears in both the image and text?"

## Next Steps

- Explore the web UI features
- Try different file types
- Check system statistics
- Review the documentation in `docs/`

## Getting Help

If you encounter issues:
1. Check `docs/SETUP.md` for detailed setup
2. Review error messages in terminal
3. Verify Docker services are running
4. Ensure API key is correctly set in `.env`
