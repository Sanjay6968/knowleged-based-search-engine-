Knowledge-base Search Engine with RAG
A full-stack Retrieval-Augmented Generation (RAG) system that allows users to upload documents and search them using natural language queries with LLM-powered answer synthesis.

Features

Document Upload: Support for PDF, TXT, and DOCX files
Smart Chunking: Automatic text splitting with overlapping windows
Semantic Search: Vector embeddings using sentence-transformers
RAG Pipeline: Combines retrieval with LLM generation
Modern UI: Beautiful, responsive React frontend
REST API: Clean backend API for all operations
Confidence Scoring: Shows answer reliability
Source Attribution: Tracks which documents were used

 Architecture
┌─────────────┐
│   Frontend  │ (React)
│   (Port 3000)│
└──────┬──────┘
       │ HTTP REST API
       │
┌──────▼──────┐
│   Backend   │ (Flask)
│   (Port 5000)│
