# 🔍 Knowledge-base Search Engine with RAG

A full-stack **Retrieval-Augmented Generation (RAG)** system that enables intelligent document search and question-answering using semantic search and AI-powered answer synthesis.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🎯 Features

### Core Functionality
-  **Multi-format Document Support** - Upload PDF, TXT, and DOCX files
-  **Semantic Search** - Vector embeddings for intelligent retrieval
-  **AI-Powered Answers** - LLM synthesis using Groq/OpenAI APIs
  **Confidence Scoring** - Real-time answer reliability metrics
-  **Source Attribution** - Track which documents informed each answer
-  **Document Management** - Add, remove, and manage your knowledge base

### Technical Features
-  **Fast Embeddings** - sentence-transformers for efficient vectorization
-  **Smart Chunking** - Overlapping text windows for better context
-  **Fallback Mechanism** - Works even without API keys
-  **Session Persistence** - Maintains document index during runtime
-  **Modern UI** - Beautiful, responsive React interface

---

## 🏗️ Architecture

```
┌─────────────────────┐
│   React Frontend    │  (Port 3000)
│   - Document Upload │
│   - Search Interface│
│   - Results Display │
└──────────┬──────────┘
           │ HTTP REST API
           │
┌──────────▼──────────┐
│   Flask Backend     │  (Port 5000)
│   - Document Ingest │
│   - Vector Storage  │
│   - RAG Pipeline    │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │             │
┌───▼────┐   ┌───▼────┐
│Sentence│   │  Groq  │
│Transform│   │  API   │
│  Model │   │(LLM)   │
└────────┘   └────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+**
- **Node.js 14+**
- **npm or yarn**
- **Groq API Key** (free at https://console.groq.com) or OpenAI API Key

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/rag-search-engine.git
cd rag-search-engine
```

#### 2. Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# Run backend
python app.py
```

Backend will run on **http://localhost:5000**

#### 3. Frontend Setup
```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Run frontend
npm start
```

Frontend will open automatically at **http://localhost:3000**

---

## 🔑 Getting API Keys

### Option 1: Groq (Recommended - Free & Fast)
1. Visit https://console.groq.com
2. Sign up with Google/GitHub
3. Navigate to "API Keys"
4. Create new key
5. Copy key (starts with `gsk_...`)

### Option 2: OpenAI (Free Trial)
1. Visit https://platform.openai.com/signup
2. Verify phone number
3. Go to API Keys section
4. Create new secret key
5. Copy key (starts with `sk-...`)

### Add to .env file:
```bash
# For Groq (recommended)
GROQ_API_KEY=gsk_your_key_here

# OR for OpenAI
OPENAI_API_KEY=sk_your_key_here

# Optional
FLASK_ENV=development
```

---

## 📖 Usage Guide

### 1. Upload Documents
- Click "Click to upload documents"
- Select PDF, TXT, or DOCX files
- Wait for processing (shows chunk count)
- Document appears in "Documents" list

### 2. Search & Ask Questions
- Type your question in the search box
- Press Enter or click "Search"
- View AI-generated answer with confidence score
- Check sources used for the answer

### 3. Example Queries

**Good Questions (High Confidence):**
```
Who created Python?
When was the company founded?
What are the key features mentioned?
List the main benefits of X
How does Y work according to the document?
```

**Avoid Vague Questions (Low Confidence):**
```
Tell me everything
What is this about?
Summarize
Is this good?
```

---

## 🛠️ API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### Health Check
```http
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-17T11:22:28.962814",
  "documents_indexed": 3
}
```

#### Upload Documents
```http
POST /api/upload
Content-Type: multipart/form-data
```
**Body:** Form data with file(s)

**Response:**
```json
{
  "success": [
    {
      "id": "0",
      "name": "document.pdf",
      "size": 51200,
      "processed": true,
      "chunks": 15,
      "uploaded_at": "2025-10-17T11:30:00"
    }
  ],
  "errors": [],
  "total_documents": 1
}
```

#### Search Query
```http
POST /api/search
Content-Type: application/json
```
**Body:**
```json
{
  "query": "What is machine learning?",
  "top_k": 5
}
```

**Response:**
```json
{
  "query": "What is machine learning?",
  "answer": "Machine learning is a subset of AI...",
  "sources": ["document.pdf"],
  "confidence": 0.87,
  "retrieved_chunks": [...],
  "timestamp": "2025-10-17T11:35:00"
}
```

#### List Documents
```http
GET /api/documents
```

#### Delete Document
```http
DELETE /api/documents/{doc_id}
```

#### Clear All Documents
```http
POST /api/clear
```

---

## 📁 Project Structure

```
rag-search-engine/
├── backend/
│   ├── app.py                 # Flask application
│   ├── rag_engine.py          # RAG implementation
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables
│   ├── uploads/               # Uploaded documents
│   └── venv/                  # Virtual environment
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.css           # Styling
│   │   └── index.js          # Entry point
│   ├── package.json
│   └── node_modules/
│
└── README.md
```

---

## 🔬 Technical Details

### RAG Pipeline

1. **Document Ingestion**
   - Extract text from PDF/TXT/DOCX
   - Split into overlapping chunks (500 words, 50 overlap)
   - Generate embeddings using sentence-transformers

2. **Query Processing**
   - Encode user query to vector
   - Calculate cosine similarity with all chunks
   - Retrieve top-k most relevant chunks

3. **Answer Generation**
   - Format retrieved chunks as context
   - Send to LLM (Groq/OpenAI) with prompt
   - Return synthesized answer with confidence score

### Models Used

- **Embedding Model:** `all-MiniLM-L6-v2` (384 dimensions)
- **LLM:** `llama-3.1-8b-instant` (Groq) or `gpt-3.5-turbo` (OpenAI)

### Confidence Scoring

```python
# Weighted average of similarity scores
weights = [1.0, 0.8, 0.6, 0.4, 0.2]
confidence = weighted_average(similarities, weights)

# Boost if top chunk is highly relevant
if top_similarity > 0.7:
    confidence *= 1.15
```

---

## ⚙️ Configuration

### Backend Configuration

**requirements.txt:**
```txt
flask==2.3.0
flask-cors==4.0.0
sentence-transformers==2.2.2
requests==2.31.0
PyPDF2==3.0.1
python-docx==0.8.11
numpy==1.24.3
scikit-learn==1.3.0
werkzeug==2.3.0
python-dotenv==1.0.0
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for LLM | No* |
| `OPENAI_API_KEY` | OpenAI API key | No* |
| `FLASK_ENV` | Flask environment | No |
| `FLASK_DEBUG` | Debug mode | No |

*At least one API key recommended for best results

---

## 🧪 Testing

### Manual Testing

1. **Upload Test:**
   ```bash
   curl -X POST -F "files=@test.txt" http://localhost:5000/api/upload
   ```

2. **Search Test:**
   ```bash
   curl -X POST http://localhost:5000/api/search \
     -H "Content-Type: application/json" \
     -d '{"query":"What is Python?"}'
   ```

3. **Health Test:**
   ```bash
   curl http://localhost:5000/api/health
   ```

### Sample Test Document

Create `test.txt`:
```txt
Python is a high-level programming language created by Guido van Rossum.
It was first released in 1991 and is known for its simple, readable syntax.
Python is widely used in web development, data science, and artificial intelligence.
Popular frameworks include Django, Flask, TensorFlow, and PyTorch.
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "API Error: 401 Unauthorized"**
- Check your API key in `.env`
- Verify key is valid on Groq/OpenAI dashboard
- Restart backend after adding key

**2. "API Error: 400 Bad Request"**
- Document is too large
- Try smaller documents or shorter queries
- Update `rag_engine.py` to limit chunk size

**3. "No module named 'sentence_transformers'"**
```bash
pip install -r requirements.txt
```

**4. Low Confidence Scores**
- Use specific questions
- Match document vocabulary
- Upload more relevant documents

**5. CORS Errors**
- Ensure backend is running on port 5000
- Check `flask-cors` is installed
- Restart both frontend and backend

**6. Port Already in Use**
```bash
# Kill process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:5000 | xargs kill -9
```

---

## 🚀 Deployment

### Docker Deployment

**Dockerfile (Backend):**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./backend/uploads:/app/uploads

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

### Production Considerations

- Use PostgreSQL for document metadata
- Implement vector database (Pinecone, Weaviate)
- Add authentication & authorization
- Set up rate limiting
- Use production WSGI server (Gunicorn)
- Enable HTTPS
- Implement caching layer

---

## 📊 Performance

### Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| Document Upload (1 page) | ~2s | Includes chunking & embedding |
| Search Query | ~1-3s | With Groq API |
| Embedding Generation | ~0.5s | Per 500-word chunk |

### Optimization Tips

1. **Batch Upload:** Process multiple documents together
2. **Chunk Size:** Adjust based on document type
3. **Top-K:** Reduce to 3-5 for faster searches
4. **Caching:** Cache embeddings for repeated searches
5. **Model Selection:** Use smaller models for speed

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **sentence-transformers** - Efficient embedding generation
- **Groq** - Lightning-fast LLM inference
- **Flask** - Lightweight web framework
- **React** - Modern UI library
- **Anthropic** - For Claude assistance in development

---


## 🗺️ Roadmap

- [ ] Add support for more file formats (CSV, JSON, XML)
- [ ] Implement vector database integration
- [ ] Add user authentication
- [ ] Create document collections/folders
- [ ] Support for image/chart extraction from PDFs
- [ ] Multi-language support
- [ ] Export search results
- [ ] Advanced filtering options
- [ ] Mobile app version
- [ ] Collaborative knowledge bases

---

