import { useEffect, useRef, useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [activePage, setActivePage] = useState("Dashboard");

  // AI question-answering state
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // PDF upload state
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadError, setUploadError] = useState("");
  const [uploadedDocuments, setUploadedDocuments] = useState([]);
  const fileInputRef = useRef(null);

  const navigation = [
    { name: "Dashboard", icon: "▦" },
    { name: "AI Chat", icon: "◉" },
    { name: "Documents", icon: "▤" },
    { name: "Semantic Search", icon: "⌕" },
    { name: "Image Search", icon: "▧" },
    { name: "Agentic AI", icon: "✧" },
  ];

  const [documents, setDocuments] = useState([]);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [documentsError, setDocumentsError] = useState("");
  const [documentSearch, setDocumentSearch] = useState("");
  const [deletingDocumentId, setDeletingDocumentId] = useState(null);
  const [deleteMessage, setDeleteMessage] = useState("");
  const [deleteError, setDeleteError] = useState("");
  const [previewDocument, setPreviewDocument] = useState(null);

  // Semantic search state
  const [searchQuery, setSearchQuery] = useState("");
  const [searchTopK, setSearchTopK] = useState(5);
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);

  // Semantic image search state
  const [imageSearchQuery, setImageSearchQuery] = useState("");
  const [imageSearchTopK, setImageSearchTopK] = useState(5);
  const [imageSearchResults, setImageSearchResults] = useState([]);
  const [imageSearchLoading, setImageSearchLoading] = useState(false);
  const [imageSearchError, setImageSearchError] = useState("");
  const [imageSearchHasSearched, setImageSearchHasSearched] = useState(false);

  // Agentic AI state
  const [agentQuestion, setAgentQuestion] = useState("");
  const [agentLoading, setAgentLoading] = useState(false);
  const [agentError, setAgentError] = useState("");
  const [agentResponse, setAgentResponse] = useState(null);

  // Search document chunks by meaning using the FastAPI endpoint.
  async function handleSemanticSearch(event) {
    event.preventDefault();

   const trimmedQuery = searchQuery.trim();

    // Prevent another search while one is running.
    if (searchLoading) return;

    // Display an error when the search query is empty.
    if (!trimmedQuery) {
      setSearchError("Please enter a search query before searching.");
      setSearchResults([]);
      setHasSearched(false);
      return;
    }

    setSearchLoading(true);
    setSearchError("");
    setSearchResults([]);
    setHasSearched(true);
    setActivePage("Semantic Search");

    try {
      const response = await axios.post(
        `${API_BASE_URL}/search/`,
        {
          query: trimmedQuery,
          top_k: Number(searchTopK),
        },
        { timeout: 60000 }
      );

      setSearchResults(response.data.results || []);
    } catch (err) {
      console.error("Semantic search failed:", err);

      if (err.response) {
        const detail = err.response.data?.detail;
        setSearchError(
          typeof detail === "string"
            ? detail
            : `Search failed with status ${err.response.status}.`
        );
      } else if (err.code === "ECONNABORTED") {
        setSearchError("The search took too long. Please try again.");
      } else {
        setSearchError(
          "Cannot connect to FastAPI. Check that the backend is running."
        );
      }
    } finally {
      setSearchLoading(false);
    }
  }

  // Search AI-generated image descriptions through the FastAPI endpoint.
  async function handleImageSearch(event) {
    event.preventDefault();

    const trimmedQuery = imageSearchQuery.trim();
    if (!trimmedQuery || imageSearchLoading) return;

    setImageSearchLoading(true);
    setImageSearchError("");
    setImageSearchResults([]);
    setImageSearchHasSearched(true);
    setActivePage("Image Search");

    try {
      const response = await axios.post(
        `${API_BASE_URL}/image-search/`,
        {
          query: trimmedQuery,
          top_k: Number(imageSearchTopK),
        },
        { timeout: 60000 }
      );

      setImageSearchResults(response.data.results || []);
    } catch (err) {
      console.error("Image search failed:", err);

      if (err.response) {
        const detail = err.response.data?.detail;
        setImageSearchError(
          typeof detail === "string"
            ? detail
            : `Image search failed with status ${err.response.status}.`
        );
      } else if (err.code === "ECONNABORTED") {
        setImageSearchError("Image search took too long. Please try again.");
      } else {
        setImageSearchError(
          "Cannot connect to FastAPI. Check that the backend is running."
        );
      }
    } finally {
      setImageSearchLoading(false);
    }
  }

  // Send a question to the Agentic AI backend.
async function handleAgentQuestion(event) {
  event.preventDefault();

  const question = agentQuestion.trim();

  if (!question || agentLoading) {
    return;
  }

  setAgentLoading(true);
  setAgentError("");
  setAgentResponse(null);

  try {
    const response = await axios.post(
      `${API_BASE_URL}/agent/`,
      {
        question,
        top_k: 3,
      },
      {
        timeout: 60000,
      }
    );

    setAgentResponse(response.data);
  } catch (error) {
    console.error("Agent request failed:", error);

    if (error.response) {
      const detail = error.response.data?.detail;

      setAgentError(
        typeof detail === "string"
          ? detail
          : `Agent request failed with status ${error.response.status}.`
      );
    } else if (error.code === "ECONNABORTED") {
      setAgentError("The request timed out. Please try again.");
    } else {
      setAgentError(
        "Cannot connect to the backend. Check that FastAPI is running."
      );
    }
  } finally {
    setAgentLoading(false);
  }
}

  // Send a question to the FastAPI backend.
  async function handleAskAI(event) {
    event.preventDefault();

    const trimmedQuestion = question.trim();
    if (!trimmedQuestion || loading) return;

    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);
    setActivePage("AI Chat");

    try {
      const response = await axios.post(
        `${API_BASE_URL}/ask/`,
        {
          question: trimmedQuestion,
          top_k: 3,
        },
        {
          timeout: 120000,
        }
      );

      setAnswer(response.data.answer || "No answer was returned.");
      setSources(response.data.sources || []);
    } catch (err) {
      console.error("AI request failed:", err);

      if (err.response) {
        const detail = err.response.data?.detail;
        setError(
          typeof detail === "string"
            ? detail
            : `The server returned an error (${err.response.status}).`
        );
      } else if (err.code === "ECONNABORTED") {
        setError("The request took too long. Please try again.");
      } else {
        setError(
          "Cannot connect to FastAPI. Check that the backend is running."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  // Upload a PDF to the existing FastAPI endpoint.
  async function handleUpload(event) {
    event.preventDefault();

    if (!selectedFile || uploading) {
      setUploadError("Please select a PDF file first.");
      return;
    }

    const isPdf =
      selectedFile.type === "application/pdf" ||
      selectedFile.name.toLowerCase().endsWith(".pdf");

    if (!isPdf) {
      setUploadError("Please select a PDF file.");
      return;
    }

    setUploading(true);
    setUploadMessage("");
    setUploadError("");

    const formData = new FormData();
    // The existing FastAPI endpoint expects the multipart field named "file".
    formData.append("file", selectedFile);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/documents/upload`,
        formData,
        {
          timeout: 120000,
        }
      );

      const document = response.data;
      setUploadMessage(
        document.message ||
          `Successfully processed ${document.filename || selectedFile.name}.`
      );

      setUploadedDocuments((previous) => {
        const withoutDuplicate = previous.filter(
          (item) => item.document_id !== document.document_id
        );
        return [document, ...withoutDuplicate];
      });

      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      await loadDocuments();
    } catch (err) {
      console.error("PDF upload failed:", err);

      if (err.response) {
        const detail = err.response.data?.detail;
        setUploadError(
          typeof detail === "string"
            ? detail
            : `Upload failed with status ${err.response.status}.`
        );
      } else if (err.code === "ECONNABORTED") {
        setUploadError(
          "PDF processing took too long. Check the backend terminal before trying again."
        );
      } else {
        setUploadError(
          "Cannot connect to FastAPI. Check that the backend is running."
        );
      }
    } finally {
      setUploading(false);
    }
  }
  async function loadDocuments() {
    setDocumentsLoading(true);
    setDocumentsError("");

    try {
      const response = await axios.get(
        `${API_BASE_URL}/documents/`,
        { timeout: 15000 }
      );

      setDocuments(response.data.documents || []);
    } catch (err) {
      console.error("Failed to load documents:", err);

      setDocumentsError(
        err.response?.data?.detail ||
          "Unable to load documents. Check that FastAPI is running."
      );
    } finally {
      setDocumentsLoading(false);
    }
  }

  async function handleDeleteDocument(document) {
    if (!document?.document_id || deletingDocumentId) return;

    const confirmed = window.confirm(
      `Permanently delete "${document.filename}"? This removes its PDF, search chunks, and database record.`
    );

    if (!confirmed) return;

    setDeletingDocumentId(document.document_id);
    setDeleteMessage("");
    setDeleteError("");

    try {
      const response = await axios.delete(
        `${API_BASE_URL}/documents/${encodeURIComponent(document.document_id)}`,
        { timeout: 30000 }
      );

      setDeleteMessage(
        response.data?.message || `"${document.filename}" was deleted successfully.`
      );

      setDocuments((current) =>
        current.filter((item) => item.document_id !== document.document_id)
      );
      setUploadedDocuments((current) =>
        current.filter((item) => item.document_id !== document.document_id)
      );

      // Remove stale results for the deleted document from the visible search page.
      setSearchResults((current) =>
        current.filter((item) => item.document_id !== document.document_id)
      );

      await loadDocuments();
    } catch (err) {
      console.error("Document deletion failed:", err);
      const detail = err.response?.data?.detail;
      setDeleteError(
        typeof detail === "string"
          ? detail
          : err.response
            ? `Deletion failed with status ${err.response.status}.`
            : "Cannot connect to FastAPI. Check that the backend is running."
      );
    } finally {
      setDeletingDocumentId(null);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  function handleSuggestion(text) {
    setQuestion(text);
    setError("");
  }

  function handleFileSelection(event) {
    const file = event.target.files?.[0] || null;
    setSelectedFile(file);
    setUploadMessage("");
    setUploadError("");
  }

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">O</div>
          <div>
            <h2>OmniInsight</h2>
            <span>AI Intelligence Platform</span>
          </div>
        </div>

        <div className="workspace-label">WORKSPACE</div>

        <nav className="navigation" aria-label="Main navigation">
          {navigation.map((item) => (
            <button
              key={item.name}
              type="button"
              className={`nav-item ${
                activePage === item.name ? "active" : ""
              }`}
              onClick={() => setActivePage(item.name)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.name}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="status-indicator">
            <span className="status-dot"></span>
            <div>
              <strong>AI Engine</strong>
              <small>Ready to assist</small>
            </div>
          </div>

          <div className="profile">
            <div className="avatar">C</div>
            <div>
              <strong>Workspace User</strong>
              <small>Personal workspace</small>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="breadcrumb">Workspace / </span>
            <strong>{activePage}</strong>
          </div>

          <div className="topbar-right">
            <span className="system-status">
              <span className="status-dot"></span>
              AI Workspace
            </span>
            <div className="avatar">C</div>
          </div>
        </header>

        <div className="page-content">
          {activePage === "AI Chat" ? (
            <section className="ai-chat-page">
              <div className="documents-page-header">
                <div>
                  <span className="section-label">RETRIEVAL-AUGMENTED GENERATION</span>
                  <h1>AI Chat</h1>
                  <p>Ask questions about your uploaded PDFs and get answers grounded in your knowledge base.</p>
                </div>
              </div>

              <div className="panel ask-panel ai-chat-panel">
                <div className="panel-heading">
                  <div>
                    <span className="panel-label">AI ASSISTANT</span>
                    <h2>Ask your knowledge base</h2>
                    <p>Answers are generated using relevant passages from your documents.</p>
                  </div>
                  <div className="panel-heading-icon" aria-hidden="true">✳</div>
                </div>

                <form className="question-form" onSubmit={handleAskAI}>
                  <textarea
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    placeholder="Ask a question about your documents..."
                    rows={5}
                    maxLength={2000}
                    disabled={loading}
                    aria-label="Question about your documents"
                  />
                  <div className="question-footer">
                    <span>Answers with document references</span>
                    <button
                      className="primary-button"
                      type="submit"
                      disabled={!question.trim() || loading}
                    >
                      {loading ? "Thinking..." : "Ask AI"}
                      <span>{loading ? "..." : "↗"}</span>
                    </button>
                  </div>
                </form>

                {loading && (
                  <div className="response-message loading-message" role="status">
                    Searching your documents and generating an answer...
                  </div>
                )}
                {error && (
                  <div className="response-message error-message" role="alert">{error}</div>
                )}

                {answer && (
                  <div className="answer-panel">
                    <div className="answer-heading">
                      <span className="answer-icon" aria-hidden="true">✳</span>
                      <h3>AI Answer</h3>
                    </div>
                    <div className="answer-text">
                      <ReactMarkdown>{answer}</ReactMarkdown>
                    </div>
                    <div className="sources-section">
                      <h4>Retrieved Sources</h4>
                      {sources.length > 0 ? (
                        sources.map((source, index) => (
                          <div
                            className="source-item"
                            key={`${source.filename || "source"}-${source.page ?? "unknown"}-${index}`}
                          >
                            <span className="source-number">{index + 1}</span>
                            <div>
                              <strong>{source.filename || "Document source"}</strong>
                              <small>{source.page != null ? `Page ${source.page}` : "Page not specified"}</small>
                            </div>
                          </div>
                        ))
                      ) : (
                        <p className="no-sources">No source references were returned.</p>
                      )}
                    </div>
                  </div>
                )}

                <div className="suggestions">
                  <span>Try asking</span>
                  <button type="button" onClick={() => handleSuggestion("Summarize my uploaded documents")} disabled={loading}>
                    Summarize documents
                  </button>
                  <button type="button" onClick={() => handleSuggestion("What are the key findings?")} disabled={loading}>
                    Find key findings
                  </button>
                  <button type="button" onClick={() => handleSuggestion("Explain the main concepts in my documents")} disabled={loading}>
                    Explain main concepts
                  </button>
                </div>
              </div>
            </section>
          ) : activePage === "Documents" ? (
            <section className="documents-page">
              <div className="documents-page-header">
                <div>
                  <span className="section-label">DOCUMENT LIBRARY</span>
                  <h1>Your Documents</h1>
                  <p>
                    Browse and search documents stored in your knowledge base.
                  </p>
                </div>

                <button
                  type="button"
                  className="refresh-documents-button"
                  onClick={loadDocuments}
                  disabled={documentsLoading}
                >
                  {documentsLoading ? "Refreshing..." : "↻ Refresh"}
                </button>
              </div>

              <div className="documents-summary">
                <div>
                  <span>Total documents</span>
                  <strong>{documents.length}</strong>
                </div>
                <div>
                  <span>Total pages</span>
                  <strong>
                    {documents.reduce(
                      (total, document) =>
                        total + Number(document.total_pages || 0),
                      0
                    )}
                  </strong>
                </div>
                <div>
                  <span>Processed</span>
                  <strong>
                    {
                      documents.filter(
                        (document) => document.status === "processed"
                      ).length
                    }
                  </strong>
                </div>
              </div>

              <div className="documents-toolbar">
                <input
                  type="search"
                  value={documentSearch}
                  onChange={(event) => setDocumentSearch(event.target.value)}
                  placeholder="Search documents by filename..."
                  aria-label="Search documents by filename"
                />
              </div>

              {documentsLoading && (
                <div className="documents-message" role="status">
                  Loading documents from PostgreSQL...
                </div>
              )}

              {documentsError && (
                <div className="upload-error" role="alert">
                  {documentsError}
                </div>
              )}

              {deleteMessage && (
                <div className="upload-success" role="status">
                  {deleteMessage}
                </div>
              )}

              {deleteError && (
                <div className="upload-error" role="alert">
                  {deleteError}
                </div>
              )}

              {!documentsLoading && !documentsError && (
                <div className="documents-table-wrapper">
                  <table className="documents-table">
                    <thead>
                      <tr>
                        <th>Document</th>
                        <th>Pages</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {documents
                        .filter((document) =>
                          document.filename
                            ?.toLowerCase()
                            .includes(documentSearch.trim().toLowerCase())
                        )
                        .map((document) => (
                          <tr key={document.document_id}>
                            <td>
                              <div className="document-table-name">
                                <span className="pdf-badge">PDF</span>
                                <div>
                                  <strong>{document.filename}</strong>
                                  <small>ID: {document.document_id}</small>
                                </div>
                              </div>
                            </td>
                            <td>{document.total_pages ?? "—"}</td>
                            <td>
                              <span
                                className={`document-status-badge ${
                                  document.status === "processed"
                                    ? "processed"
                                    : "pending"
                                }`}
                              >
                                {document.status || "unknown"}
                              </span>
                            </td>
                            <td>
                              <div className="document-action-buttons">
                                <button
                                  type="button"
                                  className="preview-document-button"
                                  onClick={() => setPreviewDocument(document)}
                                  aria-label={`Preview ${document.filename}`}
                                >
                                  Preview
                                </button>
                                <button
                                  type="button"
                                  className="delete-document-button"
                                onClick={() => handleDeleteDocument(document)}
                                disabled={deletingDocumentId !== null}
                                aria-label={`Delete ${document.filename}`}
                              >
                                  {deletingDocumentId === document.document_id
                                    ? "Deleting..."
                                    : "Delete"}
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}

                      {documents.filter((document) =>
                        document.filename
                          ?.toLowerCase()
                          .includes(documentSearch.trim().toLowerCase())
                      ).length === 0 && (
                        <tr>
                          <td colSpan="4" className="documents-empty">
                            {documents.length === 0
                              ? "No documents have been uploaded yet."
                              : "No documents match your search."}
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          ) : activePage === "Image Search" ? (
            <section className="image-search-page">
              <div className="documents-page-header">
                <div>
                  <span className="section-label">MULTIMODAL RETRIEVAL</span>
                  <h1>Image Search</h1>
                  <p>
                    Find images inside indexed PDFs by describing what you see.
                    Search runs against AI-generated image descriptions.
                  </p>
                </div>
              </div>

              <div className="image-search-panel">
                <div className="panel-heading">
                  <div>
                    <span className="panel-label">VISUAL KNOWLEDGE BASE</span>
                    <h2>What image are you looking for?</h2>
                    <p>
                      Describe a scene, object, chart, diagram, or other visual detail.
                    </p>
                  </div>
                  <div className="panel-heading-icon" aria-hidden="true">▧</div>
                </div>

                <form className="image-search-form" onSubmit={handleImageSearch}>
                  <input
                    type="search"
                    value={imageSearchQuery}
                    onChange={(event) => setImageSearchQuery(event.target.value)}
                    placeholder="Example: industrial structures with glowing blue lights"
                    aria-label="Search indexed images"
                    maxLength={1000}
                    disabled={imageSearchLoading}
                  />

                  <div className="image-search-controls">
                    <label htmlFor="image-search-top-k">Results to retrieve</label>
                    <select
                      id="image-search-top-k"
                      value={imageSearchTopK}
                      onChange={(event) => setImageSearchTopK(Number(event.target.value))}
                      disabled={imageSearchLoading}
                    >
                      <option value={3}>3 results</option>
                      <option value={5}>5 results</option>
                      <option value={10}>10 results</option>
                      <option value={20}>20 results</option>
                    </select>
                    <button
                      type="submit"
                      className="primary-button"
                      disabled={!imageSearchQuery.trim() || imageSearchLoading}
                    >
                      {imageSearchLoading ? "Searching..." : "Search images"}
                      <span>{imageSearchLoading ? "…" : "⌕"}</span>
                    </button>
                  </div>
                </form>

                {imageSearchLoading && (
                  <div className="response-message loading-message" role="status">
                    Searching indexed image descriptions...
                  </div>
                )}

                {imageSearchError && (
                  <div className="response-message error-message" role="alert">
                    {imageSearchError}
                  </div>
                )}

                {imageSearchHasSearched && !imageSearchLoading && !imageSearchError && (
                  <div className="image-search-results">
                    <div className="semantic-results-heading">
                      <h3>Matching images</h3>
                      <span>{imageSearchResults.length} result(s)</span>
                    </div>

                    {imageSearchResults.length > 0 ? (
                      <div className="image-results-grid">
                        {imageSearchResults.map((result, index) => (
                          <article
                            className="image-result-card"
                            key={result.image_id || `${result.document_id}-${result.page}-${index}`}
                          >
                            <div className="image-result-preview">
                              <img
                                src={`${API_BASE_URL}/images/${encodeURIComponent(
                                  (result.image_path || "").replace(/\\/g, "/").split("/").pop()
                                )}`}
                                alt={result.description || `Image from PDF page ${result.page}`}
                                loading="lazy"
                                onError={(event) => {
                                  event.currentTarget.style.display = "none";
                                }}
                              />
                            </div>
                            <div className="image-result-content">
                              <div className="image-result-meta">
                                <span className="image-page-badge">
                                  PDF page {result.page ?? "—"}
                                </span>
                                {result.distance != null && (
                                  <small>Distance: {Number(result.distance).toFixed(4)}</small>
                                )}
                              </div>
                              <p>{result.description || "No image description was returned."}</p>
                              <details>
                                <summary>Image details</summary>
                                <small>Image ID: {result.image_id || "—"}</small>
                                <small>Document ID: {result.document_id || "—"}</small>
                                <small className="image-path-text">
                                  Stored file: {result.image_path || "Unavailable"}
                                </small>
                              </details>
                            </div>
                          </article>
                        ))}
                      </div>
                    ) : (
                      <div className="semantic-empty">
                        No matching images were found. Try describing the visual content differently.
                      </div>
                    )}
                  </div>
                )}

                {!imageSearchHasSearched && (
                  <div className="semantic-hint">
                    <strong>Try a sample query</strong>
                    <button
                      type="button"
                      onClick={() => setImageSearchQuery("industrial structures with glowing blue lights")}
                    >
                      industrial structures with glowing blue lights
                    </button>
                    <button
                      type="button"
                      onClick={() => setImageSearchQuery("city skyline at dusk")}
                    >
                      city skyline at dusk
                    </button>
                    <button
                      type="button"
                      onClick={() => setImageSearchQuery("coral reef and tropical fish")}
                    >
                      coral reef and tropical fish
                    </button>
                  </div>
                )}
              </div>
            </section>
          ) : activePage === "Agentic AI" ? (
  <section className="agentic-ai-page">
    <div className="documents-page-header">
      <div>
        <span className="section-label">AUTONOMOUS TOOL SELECTION</span>
        <h1>Agentic AI</h1>
        <p>
          Ask questions about your documents or search for relevant images.
          Your AI agent selects the appropriate tool.
        </p>
      </div>
    </div>

    <div className="agentic-ai-panel">
      <div className="panel-heading">
        <div>
          <span className="panel-label">AI AGENT</span>
          <h2>What would you like to explore?</h2>
          <p>Ask a question about your knowledge base.</p>
        </div>
      </div>

      <form onSubmit={handleAgentQuestion}>
        <textarea
          value={agentQuestion}
          onChange={(event) => setAgentQuestion(event.target.value)}
          placeholder="Example: Find images of colorful planets and stars..."
          rows={4}
          maxLength={1000}
          required
          disabled={agentLoading}
        />

        <div className="agentic-ai-form-footer">
          <span>Ask about documents or search for images.</span>

          <button
            type="submit"
            disabled={agentLoading || !agentQuestion.trim()}
          >
            {agentLoading ? "Working..." : "Ask Agent"}
          </button>
        </div>
      </form>

      {agentError && (
        <div className="error-message" role="alert">
          {agentError}
        </div>
      )}

      {agentResponse && (
        <div className="agentic-ai-response">
          <h3>Agent Response</h3>

          {agentResponse.selected_tool && (
            <p>
              <strong>Selected tool:</strong>{" "}
              {agentResponse.selected_tool}
            </p>
          )}

          {agentResponse.message && <p>{agentResponse.message}</p>}

          {agentResponse.result && (
  agentResponse.selected_tool === "image_search" &&
  Array.isArray(agentResponse.result.results) ? (
    <div className="agent-image-results">
      <p>
        Found {agentResponse.result.results_count ?? 0} matching images.
      </p>

      <div className="agent-image-grid">
        {agentResponse.result.results.map((image, index) => {
  const imageFilename = image.image_path
    ? image.image_path.split(/[\\/]/).pop()
    : "";

  const sourceDocument = documents.find(
    (document) => document.document_id === image.document_id
  );

  return (
    <article
      className="agent-image-card"
      key={image.image_id || index}
    >
      <img
        src={`${API_BASE_URL}/images/${encodeURIComponent(imageFilename)}`}
        alt={image.description || "Extracted document image"}
        loading="lazy"
      />

      <div className="agent-image-card-content">
        <span className="image-page-badge">
          PDF page {image.page ?? "Unknown"}
        </span>

        <p className="agent-image-filename">
          <strong>Source PDF:</strong>{" "}
          {sourceDocument?.filename || image.filename || "Uploaded PDF"}
        </p>

        <button
  type="button"
  className="agent-view-pdf-button"
  onClick={() => {
    if (image.document_id) {
      setPreviewDocument({
        document_id: image.document_id,
        filename:
          sourceDocument?.filename ||
          image.filename ||
          "Uploaded PDF",
      });
    }
  }}
  disabled={!image.document_id}
>
  View PDF
  <span aria-hidden="true"> ↗</span>
</button>

        <p>
          {image.description || "No description available."}
        </p>

        {image.distance != null && (
          <small>
            Search distance: {Number(image.distance).toFixed(4)}
          </small>
        )}

        {sourceDocument && (
          <button
            type="button"
            className="agent-view-pdf-button"
            onClick={() => setPreviewDocument(sourceDocument)}
          >
            View PDF
          </button>
        )}
      </div>
    </article>
  );
})}
      </div>
    </div>
  ) : (
    <pre>
      {JSON.stringify(agentResponse.result, null, 2)}
    </pre>
  )
)}
        </div>
      )}

      <div className="agentic-ai-examples">
        <strong>Try an example</strong>

        <button
          type="button"
          onClick={() =>
            setAgentQuestion(
              "What equipment and components are described in my documents?"
            )
          }
        >
          Ask about documents
        </button>

        <button
          type="button"
          onClick={() =>
            setAgentQuestion("Find images of colorful planets and stars")
          }
        >
          Find images
        </button>
      </div>
    </div>
  </section>
) : activePage === "Semantic Search" ? (
            <section className="semantic-page">
              <div className="documents-page-header">
                <div>
                  <span className="section-label">MEANING-BASED RETRIEVAL</span>
                  <h1>Semantic Search</h1>
                  <p>
                    Find relevant passages in your PDFs using meaning, not just
                    exact keyword matches.
                  </p>
                </div>
              </div>

              <div className="semantic-search-panel">
                <div className="panel-heading">
                  <div>
                    <span className="panel-label">KNOWLEDGE BASE SEARCH</span>
                    <h2>What would you like to find?</h2>
                    <p>
                      Search across text chunks indexed in your ChromaDB
                      knowledge base.
                    </p>
                  </div>
                  <div className="panel-heading-icon" aria-hidden="true">⌕</div>
                </div>

                <form
                  className="semantic-search-form"
                  onSubmit={handleSemanticSearch}
                >
                  <input
                    type="search"
                    value={searchQuery}
                    onChange={(event) => setSearchQuery(event.target.value)}
                    placeholder="Example: space exploration and galaxies"
                    aria-label="Semantic search query"
                    maxLength={2000}
                    disabled={searchLoading}
                  />

                  <div className="semantic-search-controls">
                    <label htmlFor="search-top-k">Results to retrieve</label>
                    <select
                      id="search-top-k"
                      value={searchTopK}
                      onChange={(event) => setSearchTopK(Number(event.target.value))}
                      disabled={searchLoading}
                    >
                      <option value={3}>3 results</option>
                      <option value={5}>5 results</option>
                      <option value={10}>10 results</option>
                    </select>

                    <button
                      type="submit"
                      className="primary-button"
                      disabled={!searchQuery.trim() || searchLoading}
                    >
                      {searchLoading ? "Searching..." : "Search documents"}
                      <span>{searchLoading ? "…" : "⌕"}</span>
                    </button>
                  </div>
                </form>

                {searchLoading && (
                  <div className="response-message loading-message" role="status">
                    Searching your indexed document chunks...
                  </div>
                )}

                {searchError && (
                  <div className="response-message error-message" role="alert">
                    {searchError}
                  </div>
                )}

                {hasSearched && !searchLoading && !searchError && (
                  <div className="semantic-results">
                    <div className="semantic-results-heading">
                      <h3>Search results</h3>
                      <span>{searchResults.length} result(s)</span>
                    </div>

                    {searchResults.length > 0 ? (
                      searchResults.map((result, index) => (
                        <article
                          className="semantic-result-card"
                          key={`${result.document_id || result.filename || "result"}-${result.page ?? "page"}-${index}`}
                        >
                          <div className="semantic-result-top">
                            <span className="source-number">{index + 1}</span>
                            <div className="semantic-result-meta">
                              <strong>{result.filename || "Document source"}</strong>
                              <small>
                                {result.page != null ? `Page ${result.page}` : "Page not specified"}
                                {result.distance != null
                                  ? ` · Distance: ${Number(result.distance).toFixed(4)}`
                                  : ""}
                              </small>
                            </div>
                          </div>
                          <p>{result.text || "No text was returned for this result."}</p>
                        </article>
                      ))
                    ) : (
                      <div className="semantic-empty">
                        No matching passages were found. Try a different query or
                        upload a text-based PDF first.
                      </div>
                    )}
                  </div>
                )}

                {!hasSearched && (
                  <div className="semantic-hint">
                    <strong>Try a sample query</strong>
                    <button
                      type="button"
                      onClick={() => setSearchQuery("space exploration and galaxies")}
                    >
                      space exploration and galaxies
                    </button>
                    <button
                      type="button"
                      onClick={() => setSearchQuery("nature landscape")}
                    >
                      nature landscape
                    </button>
                  </div>
                )}
              </div>
            </section>
          ) : (
            <>
          {/* Welcome section */}
          <section className="welcome-section">
            <div>
              <div className="eyebrow">INTELLIGENT DOCUMENT ANALYSIS</div>
              <h1>
                Your knowledge,
                <br />
                <span>amplified by AI.</span>
              </h1>
              <p>
                Explore your documents, uncover insights, and get answers
                backed by your own knowledge base.
              </p>
            </div>

            <div className="hero-visual" aria-hidden="true">
              <div className="orbit orbit-one"></div>
              <div className="orbit orbit-two"></div>
              <div className="ai-core">
                <span>✳</span>
              </div>
              <div className="floating-card card-one">RAG</div>
              <div className="floating-card card-two">AI</div>
              <div className="floating-card card-three">⌘</div>
            </div>
          </section>

          {/* Statistics */}
          <section className="stats-grid">
            <div className="stat-card">
              <div className="stat-top">
                <span>Documents uploaded this session</span>
                <span className="stat-icon purple">▤</span>
              </div>
              <h2>{uploadedDocuments.length}</h2>
              <p>Successfully uploaded in this browser session</p>
            </div>

            <div className="stat-card">
              <div className="stat-top">
                <span>Indexed chunks this session</span>
                <span className="stat-icon blue">◈</span>
              </div>
              <h2>
                {uploadedDocuments.reduce(
                  (total, document) =>
                    total + Number(document.chunks_created || 0),
                  0
                )}
              </h2>
              <p>Chunks reported by recent uploads</p>
            </div>

            <div className="stat-card">
              <div className="stat-top">
                <span>AI engine</span>
                <span className="stat-icon green">✳</span>
              </div>
              <h2 className="ready-text">Ready</h2>
              <p>Answer generation configured</p>
            </div>
          </section>

          {/* PDF upload */}
          <section className="upload-panel" aria-labelledby="upload-heading">
            <div className="upload-header">
              <div>
                <span className="section-label">DOCUMENT MANAGEMENT</span>
                <h2 id="upload-heading">Upload your documents</h2>
                <p>
                  Upload a PDF to extract its text and add it to your searchable
                  knowledge base.
                </p>
              </div>
              <span className="upload-icon" aria-hidden="true">
                ↑
              </span>
            </div>

            <form className="upload-form" onSubmit={handleUpload}>
              <label htmlFor="pdf-upload" className="upload-dropzone">
                <span className="upload-symbol" aria-hidden="true">
                  ＋
                </span>
                <strong>
                  {selectedFile
                    ? selectedFile.name
                    : "Choose a PDF document"}
                </strong>
                <span>
                  Click to browse your computer. PDF files only.
                </span>
                <input
                  ref={fileInputRef}
                  id="pdf-upload"
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={handleFileSelection}
                  disabled={uploading}
                />
              </label>

              {selectedFile && (
                <div className="selected-file-row">
                  <span>
                    Selected: <strong>{selectedFile.name}</strong>
                  </span>
                  <button
                    type="button"
                    className="text-button"
                    onClick={() => {
                      setSelectedFile(null);
                      if (fileInputRef.current) {
                        fileInputRef.current.value = "";
                      }
                      setUploadError("");
                      setUploadMessage("");
                    }}
                    disabled={uploading}
                  >
                    Remove
                  </button>
                </div>
              )}

              <button
                type="submit"
                className="upload-button"
                disabled={!selectedFile || uploading}
              >
                {uploading ? (
                  <>
                    <span className="button-spinner" aria-hidden="true"></span>
                    Processing PDF...
                  </>
                ) : (
                  "Upload & Process"
                )}
              </button>
            </form>

            {uploading && (
              <div className="upload-progress-message" role="status">
                Uploading the PDF and processing its contents. Please keep this
                page open.
              </div>
            )}

            {uploadMessage && (
              <div className="upload-success" role="status">
                <strong>Upload successful</strong>
                <p>{uploadMessage}</p>
                {uploadedDocuments[0] && (
                  <small>
                    {uploadedDocuments[0].total_pages ?? "—"} pages ·{" "}
                    {uploadedDocuments[0].chunks_created ?? "—"} chunks created
                  </small>
                )}
              </div>
            )}

            {uploadError && (
              <div className="upload-error" role="alert">
                {uploadError}
              </div>
            )}

            {uploadedDocuments.length > 0 && (
              <div className="uploaded-list">
                <div className="uploaded-list-heading">
                  <h3>Recently uploaded</h3>
                  <span>{uploadedDocuments.length} this session</span>
                </div>

                {uploadedDocuments.map((document, index) => (
                  <div
                    className="uploaded-document"
                    key={
                      document.document_id ||
                      `${document.filename || "document"}-${index}`
                    }
                  >
                    <span className="pdf-badge">PDF</span>
                    <div className="uploaded-document-info">
                      <strong>{document.filename || "Uploaded PDF"}</strong>
                      <small>
                        {document.total_pages ?? "—"} pages ·{" "}
                        {document.chunks_created ?? "—"} chunks ·{" "}
                        {document.status || "processed"}
                      </small>
                    </div>
                    <span className="document-status">Ready</span>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Dashboard shortcuts */}
          <section className="workspace-grid">
                      {/* Capabilities */}
            <div className="panel capabilities-panel">
              <div className="panel-heading">
                <div>
                  <span className="panel-label">YOUR WORKSPACE</span>
                  <h2>Explore capabilities</h2>
                </div>
              </div>

              <button
                type="button"
                className="capability-item"
                onClick={() => {
                  setActivePage("Documents");
                  document
                    .getElementById("upload-heading")
                    ?.scrollIntoView({ behavior: "smooth", block: "start" });
                }}
              >
                <div className="capability-icon purple">▤</div>
                <div>
                  <strong>Document intelligence</strong>
                  <p>Upload and analyze PDF documents</p>
                </div>
                <span className="arrow">↗</span>
              </button>

              <button
                type="button"
                className="capability-item"
                onClick={() => setActivePage("Semantic Search")}
              >
                <div className="capability-icon blue">⌕</div>
                <div>
                  <strong>Semantic search</strong>
                  <p>Find information by meaning</p>
                </div>
                <span className="arrow">↗</span>
              </button>

              <button
                type="button"
                className="capability-item"
                onClick={() => {
                  setActivePage("AI Chat");
                  document
                    .querySelector(".question-form textarea")
                    ?.focus();
                }}
              >
                <div className="capability-icon green">✳</div>
                <div>
                  <strong>AI-powered answers</strong>
                  <p>Ask questions and explore insights</p>
                </div>
                <span className="arrow">↗</span>
              </button>
            </div>
          </section>

          <footer className="footer">
            <span>OmniInsight AI</span>
            <span>Intelligence grounded in your documents.</span>
          </footer>
            </>
          )}
        </div>

        {previewDocument && (
          <div
            className="pdf-preview-overlay"
            role="presentation"
            onMouseDown={(event) => {
              if (event.target === event.currentTarget) {
                setPreviewDocument(null);
              }
            }}
          >
            <section
              className="pdf-preview-modal"
              role="dialog"
              aria-modal="true"
              aria-labelledby="pdf-preview-title"
            >
              <header className="pdf-preview-header">
                <div>
                  <span className="section-label">DOCUMENT PREVIEW</span>
                  <h2 id="pdf-preview-title">{previewDocument.filename}</h2>
                </div>
                <button
                  type="button"
                  className="pdf-preview-close"
                  onClick={() => setPreviewDocument(null)}
                  aria-label="Close PDF preview"
                >
                  ×
                </button>
              </header>
              <iframe
                className="pdf-preview-frame"
                title={`Preview of ${previewDocument.filename}`}
                src={`${API_BASE_URL}/documents/${encodeURIComponent(
                  previewDocument.document_id
                )}/preview`}
              />
            </section>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
