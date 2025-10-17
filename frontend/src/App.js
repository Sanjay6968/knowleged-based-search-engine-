import React, { useState } from 'react';
import axios from 'axios';
import { Search, Upload, FileText, Loader2, AlertCircle, CheckCircle2, Trash2, Database } from 'lucide-react';
import './App.css';

const API_URL = 'http://localhost:5000/api';

function App() {
  const [documents, setDocuments] = useState([]);
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [searchHistory, setSearchHistory] = useState([]);

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (response.data.success) {
        setDocuments(prev => [...prev, ...response.data.success]);
        setError(null);
      }
      
      if (response.data.errors && response.data.errors.length > 0) {
        setError(`Some files failed: ${response.data.errors.map(e => e.filename).join(', ')}`);
      }
    } catch (err) {
      setError('Failed to upload documents. Please try again.');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    if (documents.length === 0) {
      setError('Please upload at least one document first');
      return;
    }

    setLoading(true);
    setError(null);
    setAnswer(null);

    try {
      const response = await axios.post(`${API_URL}/search`, { query });
      
      setAnswer(response.data);
      setSearchHistory(prev => [{
        query,
        timestamp: new Date().toISOString(),
        id: Date.now()
      }, ...prev.slice(0, 9)]);
      
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to process query. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const removeDocument = async (docId) => {
    try {
      await axios.delete(`${API_URL}/documents/${docId}`);
      setDocuments(prev => prev.filter(doc => doc.id !== docId));
      if (documents.length === 1) {
        setAnswer(null);
        setSearchHistory([]);
      }
    } catch (err) {
      setError('Failed to remove document');
    }
  };

  const clearAll = async () => {
    try {
      await axios.post(`${API_URL}/clear`);
      setDocuments([]);
      setAnswer(null);
      setSearchHistory([]);
      setQuery('');
      setError(null);
    } catch (err) {
      setError('Failed to clear documents');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="app-container">
      <div className="max-width-container">
        {/* Header */}
        <div className="header">
          <div className="header-title">
            <Database className="header-icon" />
            <h1>Knowledge-base Search Engine</h1>
          </div>
          <p className="header-subtitle">RAG-powered document search with LLM synthesis</p>
        </div>

        <div className="main-grid">
          {/* Left Column - Document Management */}
          <div className="left-column">
            {/* Upload Section */}
            <div className="card">
              <h2 className="card-title">
                <Upload className="icon" />
                Upload Documents
              </h2>
              
              <label className="upload-area">
                <div className="upload-box">
                  <Upload className="upload-icon" />
                  <p className="upload-text">Click to upload documents</p>
                  <p className="upload-subtext">PDF, TXT, DOCX supported</p>
                </div>
                <input
                  type="file"
                  multiple
                  accept=".pdf,.txt,.docx"
                  onChange={handleFileUpload}
                  style={{ display: 'none' }}
                  disabled={uploading}
                />
              </label>

              {uploading && (
                <div className="loading-message">
                  <Loader2 className="icon-spin" />
                  <span>Processing documents...</span>
                </div>
              )}
            </div>

            {/* Document List */}
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">
                  <FileText className="icon" />
                  Documents ({documents.length})
                </h2>
                {documents.length > 0 && (
                  <button onClick={clearAll} className="clear-button">
                    <Trash2 className="icon-small" />
                    Clear All
                  </button>
                )}
              </div>

              <div className="document-list">
                {documents.length === 0 ? (
                  <p className="empty-state">No documents uploaded yet</p>
                ) : (
                  documents.map(doc => (
                    <div key={doc.id} className="document-item">
                      <FileText className="doc-icon" />
                      <div className="doc-info">
                        <p className="doc-name">{doc.name}</p>
                        <p className="doc-size">{formatFileSize(doc.size)} • {doc.chunks} chunks</p>
                      </div>
                      <button
                        onClick={() => removeDocument(doc.id)}
                        className="remove-button"
                      >
                        <Trash2 className="icon-small" />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Search History */}
            {searchHistory.length > 0 && (
              <div className="card">
                <h2 className="card-title">Recent Searches</h2>
                <div className="history-list">
                  {searchHistory.map(item => (
                    <button
                      key={item.id}
                      onClick={() => setQuery(item.query)}
                      className="history-item"
                    >
                      <p className="history-query">{item.query}</p>
                      <p className="history-time">
                        {new Date(item.timestamp).toLocaleTimeString()}
                      </p>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Search and Results */}
          <div className="right-column">
            {/* Search Box */}
            <div className="card">
              <h2 className="card-title">
                <Search className="icon" />
                Search Knowledge Base
              </h2>

              <div className="search-section">
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask a question about your documents..."
                  className="search-input"
                  rows="3"
                  disabled={loading}
                />

                <button
                  onClick={handleSearch}
                  disabled={loading || documents.length === 0}
                  className="search-button"
                >
                  {loading ? (
                    <>
                      <Loader2 className="icon-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Search className="icon" />
                      Search
                    </>
                  )}
                </button>
              </div>

              {error && (
                <div className="error-message">
                  <AlertCircle className="icon" />
                  <p>{error}</p>
                </div>
              )}
            </div>

            {/* Answer Display */}
            {answer && (
              <div className="card answer-card">
                <div className="answer-header">
                  <CheckCircle2 className="success-icon" />
                  <h2 className="card-title">Answer</h2>
                </div>

                <div className="answer-content">
                  <p className="answer-text">{answer.answer}</p>
                </div>

                <div className="answer-meta">
                  <div className="confidence-section">
                    <span className="meta-label">Confidence:</span>
                    <div className="confidence-bar">
                      <div
                        className="confidence-fill"
                        style={{ width: `${answer.confidence * 100}%` }}
                      />
                    </div>
                    <span className="confidence-value">
                      {(answer.confidence * 100).toFixed(0)}%
                    </span>
                  </div>

                  <div className="sources-section">
                    <p className="meta-label">Sources:</p>
                    <div className="sources-tags">
                      {answer.sources.map((source, idx) => (
                        <span key={idx} className="source-tag">
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Info Card */}
            {!answer && !loading && documents.length > 0 && (
              <div className="card info-card">
                <h3 className="info-title">Ready to Search</h3>
                <p className="info-text">
                  You have {documents.length} document(s) indexed. Enter your query above to search across all documents using RAG-powered semantic search.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;