# ============================================================================
# BACKEND IMPLEMENTATION - Knowledge-base Search Engine with RAG
# ============================================================================

# ----------------------------------------------------------------------------
# FILE: app.py (Main Flask Application)
# ----------------------------------------------------------------------------

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid
from rag_engine import RAGEngine

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize RAG Engine
rag_engine = RAGEngine()

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'documents_indexed': len(rag_engine.documents)
    })

@app.route('/api/upload', methods=['POST'])
def upload_documents():
    """Upload and process documents"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400
    
    results = []
    errors = []
    
    for file in files:
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                file_id = str(uuid.uuid4())
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
                
                file.save(filepath)
                
                # Process document with RAG engine
                doc_info = rag_engine.ingest_document(filepath, filename)
                
                results.append({
                    'id': file_id,
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'processed': True,
                    'chunks': doc_info['chunks'],
                    'uploaded_at': datetime.now().isoformat()
                })
            except Exception as e:
                errors.append({
                    'filename': file.filename,
                    'error': str(e)
                })
        else:
            errors.append({
                'filename': file.filename,
                'error': 'File type not allowed'
            })
    
    return jsonify({
        'success': results,
        'errors': errors,
        'total_documents': len(rag_engine.documents)
    }), 200 if not errors else 207

@app.route('/api/search', methods=['POST'])
def search():
    """Search across documents using RAG"""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': 'Query is required'}), 400
    
    query = data['query'].strip()
    if not query:
        return jsonify({'error': 'Query cannot be empty'}), 400
    
    if len(rag_engine.documents) == 0:
        return jsonify({'error': 'No documents indexed. Please upload documents first.'}), 400
    
    try:
        # Perform RAG search
        result = rag_engine.search(query, top_k=data.get('top_k', 5))
        
        return jsonify({
            'query': query,
            'answer': result['answer'],
            'sources': result['sources'],
            'confidence': result['confidence'],
            'retrieved_chunks': result['retrieved_chunks'],
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all indexed documents"""
    docs = [
        {
            'id': doc['id'],
            'name': doc['name'],
            'chunks': doc['chunks'],
            'indexed_at': doc['indexed_at']
        }
        for doc in rag_engine.documents
    ]
    return jsonify({'documents': docs, 'total': len(docs)}), 200

@app.route('/api/documents/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete a document from the index"""
    success = rag_engine.remove_document(doc_id)
    
    if success:
        return jsonify({'message': 'Document deleted successfully'}), 200
    else:
        return jsonify({'error': 'Document not found'}), 404

@app.route('/api/clear', methods=['POST'])
def clear_all():
    """Clear all documents"""
    rag_engine.clear_all()
    return jsonify({'message': 'All documents cleared'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
