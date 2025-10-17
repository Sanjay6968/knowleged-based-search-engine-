import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
from typing import List, Dict
from datetime import datetime
import PyPDF2
import docx
import requests

class RAGEngine:
    def __init__(self, embedding_model='all-MiniLM-L6-v2'):
        """Initialize RAG engine with embedding model"""
        self.embedding_model = SentenceTransformer(embedding_model)
        self.documents = []
        self.embeddings = []
        self.chunks = []
        
        # Support multiple API providers
        self.api_key = os.getenv('GROQ_API_KEY') or os.getenv('OPENAI_API_KEY')
        self.api_provider = 'groq' if os.getenv('GROQ_API_KEY') else 'openai'
        
    def extract_text_from_file(self, filepath: str) -> str:
        """Extract text from various file formats"""
        ext = filepath.lower().split('.')[-1]
        
        if ext == 'txt':
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        
        elif ext == 'pdf':
            text = []
            try:
                with open(filepath, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text.append(page.extract_text())
                return '\n'.join(text)
            except Exception as e:
                raise ValueError(f"Error reading PDF: {str(e)}")
        
        elif ext == 'docx':
            try:
                doc = docx.Document(filepath)
                return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            except Exception as e:
                raise ValueError(f"Error reading DOCX: {str(e)}")
        
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def ingest_document(self, filepath: str, filename: str) -> Dict:
        """Process and index a document"""
        text = self.extract_text_from_file(filepath)
        
        if not text.strip():
            raise ValueError("Document appears to be empty")
        
        doc_chunks = self.chunk_text(text)
        
        if not doc_chunks:
            raise ValueError("No content could be extracted from document")
        
        chunk_embeddings = self.embedding_model.encode(doc_chunks)
        
        doc_id = str(len(self.documents))
        doc_info = {
            'id': doc_id,
            'name': filename,
            'filepath': filepath,
            'chunks': len(doc_chunks),
            'indexed_at': datetime.now().isoformat()
        }
        
        self.documents.append(doc_info)
        
        for i, (chunk, embedding) in enumerate(zip(doc_chunks, chunk_embeddings)):
            self.chunks.append({
                'doc_id': doc_id,
                'doc_name': filename,
                'chunk_id': f"{doc_id}_{i}",
                'text': chunk,
                'embedding': embedding
            })
        
        return doc_info
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve most relevant chunks for a query"""
        if not self.chunks:
            return []
        
        query_embedding = self.embedding_model.encode([query])[0]
        chunk_embeddings = np.array([c['embedding'] for c in self.chunks])
        similarities = cosine_similarity([query_embedding], chunk_embeddings)[0]
        
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        relevant_chunks = []
        for idx in top_indices:
            chunk = self.chunks[idx].copy()
            chunk['similarity'] = float(similarities[idx])
            del chunk['embedding']
            relevant_chunks.append(chunk)
        
        return relevant_chunks
    
    def call_groq_api(self, prompt: str) -> str:
        """Call Groq API for answer generation"""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-8b-instant",  # Faster and more reliable
            "messages": [
                {
                    "role": "system",
                    "content": "Answer questions concisely based on the provided context."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.5,
            "max_tokens": 400
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        return response.json()['choices'][0]['message']['content']
    
    def call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API for answer generation"""
        import openai
        openai.api_key = self.api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on provided documents."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def generate_answer_simple(self, query: str, context_chunks: List[Dict]) -> str:
        """Simple answer generation without LLM (fallback)"""
        top_chunks = context_chunks[:3]
        
        answer_parts = [
            f"Based on your documents, here's what I found regarding: '{query}'\n"
        ]
        
        for i, chunk in enumerate(top_chunks, 1):
            relevance = chunk['similarity'] * 100
            answer_parts.append(
                f"\n📄 From '{chunk['doc_name']}' ({relevance:.0f}% relevant):\n"
                f"{chunk['text'][:400]}{'...' if len(chunk['text']) > 400 else ''}\n"
            )
        
        return ''.join(answer_parts)
    
    def generate_answer(self, query: str, context_chunks: List[Dict]) -> Dict:
        """Generate answer using LLM with retrieved context"""
        
        # FIXED: Limit context to avoid token limits (Groq has ~8k token limit)
        # Use only top 3 chunks and limit each chunk length
        limited_context = "\n\n".join([
            f"[{chunk['doc_name']}]: {chunk['text'][:400]}"
            for chunk in context_chunks[:3]
        ])
        
        # FIXED: Shorter, more concise prompt
        prompt = f"""Answer the question using these documents.

Context:
{limited_context}

Question: {query}

Answer briefly and clearly based on the context above."""

        try:
            if not self.api_key:
                answer = self.generate_answer_simple(query, context_chunks)
            elif self.api_provider == 'groq':
                answer = self.call_groq_api(prompt)
            else:
                answer = self.call_openai_api(prompt)
                
        except Exception as e:
            print(f"API Error: {e}")
            # Enhanced fallback
            answer = self.generate_answer_simple(query, context_chunks)
        
        # IMPROVED: Better confidence calculation
        # Weight top chunks more heavily
        weights = [1.0, 0.8, 0.6, 0.4, 0.2]
        weighted_scores = [
            chunk['similarity'] * weights[i] 
            for i, chunk in enumerate(context_chunks[:5])
        ]
        confidence = float(np.sum(weighted_scores) / np.sum(weights[:len(weighted_scores)]))
        
        # Boost confidence if top chunk is very relevant
        if context_chunks[0]['similarity'] > 0.7:
            confidence = min(confidence * 1.15, 0.99)
        
        return {
            'answer': answer,
            'confidence': confidence
        }
    
    def search(self, query: str, top_k: int = 5) -> Dict:
        """Main search function combining retrieval and generation"""
        relevant_chunks = self.retrieve_relevant_chunks(query, top_k)
        
        if not relevant_chunks:
            return {
                'answer': 'No relevant information found in the indexed documents.',
                'sources': [],
                'confidence': 0.0,
                'retrieved_chunks': []
            }
        
        result = self.generate_answer(query, relevant_chunks)
        sources = list(set([chunk['doc_name'] for chunk in relevant_chunks]))
        
        return {
            'answer': result['answer'],
            'sources': sources,
            'confidence': result['confidence'],
            'retrieved_chunks': relevant_chunks
        }
    
    def remove_document(self, doc_id: str) -> bool:
        """Remove a document from the index"""
        self.documents = [d for d in self.documents if d['id'] != doc_id]
        self.chunks = [c for c in self.chunks if c['doc_id'] != doc_id]
        return True
    
    def clear_all(self):
        """Clear all documents and embeddings"""
        self.documents = []
        self.chunks = []