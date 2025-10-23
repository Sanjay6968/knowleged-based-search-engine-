#  RAG Application

A fast and simple Retrieval-Augmented Generation system for querying your documents using natural language.

##  Features

- 📄 Upload multiple document formats (TXT, PDF, DOC, DOCX, MD)
- 🔍 Semantic search with natural language queries
- ⚡ Fast vector similarity search using FAISS
- 🎨 Beautiful web interface included
- 🌐 RESTful API for easy integration

##  Quick Start

### Installation

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install fastapi uvicorn sentence-transformers faiss-cpu python-multipart
```

### Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at `http://localhost:8000`

### Use the Web Interface

1. Open `index.html` in your browser
2. Upload documents
3. Ask questions about your documents

## 📚 API Usage

### Upload Documents
```bash
POST http://localhost:8000/ingest
Content-Type: multipart/form-data

files: [your-files]
```

### Query Documents
```bash
POST http://localhost:8000/query
Content-Type: application/json

{
  "question": "What is this document about?"
}
```

### Health Check
```bash
GET http://localhost:8000/
```

## 🔧 Configuration

Create `.env` file:

```env
ST_MODEL=sentence-transformers/all-MiniLM-L6-v2
FAISS_INDEX_PATH=./data/faiss.index
HOST=0.0.0.0
PORT=8000
TOP_K=5
```

## 🛠️ Troubleshooting

**CORS Error?** Add this to `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Import Errors?** Reinstall dependencies:

```bash
pip uninstall sentence-transformers transformers huggingface-hub -y
pip install huggingface-hub==0.24.0 transformers==4.44.0 sentence-transformers==3.0.1
```

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t rag-app .
docker run -p 8000:8000 rag-app
```

## 📝 Requirements.txt

```txt
fastapi==0.104.1
uvicorn==0.24.0
sentence-transformers==3.0.1
faiss-cpu==1.7.4
python-multipart==0.0.6
pydantic==2.5.0
transformers==4.44.0
huggingface-hub==0.24.0
