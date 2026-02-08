import { useState, useRef, useCallback, useMemo } from 'react';
import { uploadDocument, maskPII, type Detection } from './api';
import './App.css';

interface Category {
  id: string;
  label: string;
  icon: string;
  active: boolean;
}

const DEFAULT_CATEGORIES: Category[] = [
  { id: 'name', label: 'Name', icon: '👤', active: true },
  { id: 'phone', label: 'Phone', icon: '📱', active: true },
  { id: 'email', label: 'Email', icon: '📧', active: true },
  { id: 'address', label: 'Address', icon: '📍', active: true },
  { id: 'id_number', label: 'ID Number', icon: '🪪', active: true },
  { id: 'bank_card', label: 'Bank Card', icon: '💳', active: true },
  { id: 'social_media', label: 'Social Media', icon: '🌐', active: true },
];

function App() {
  const [inputText, setInputText] = useState('');
  const [maskedText, setMaskedText] = useState('');
  const [detections, setDetections] = useState<Detection[]>([]);
  const [categories, setCategories] = useState<Category[]>(DEFAULT_CATEGORIES);
  const [fileName, setFileName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [categoriesOpen, setCategoriesOpen] = useState(true);
  const [customCategory, setCustomCategory] = useState('');
  const [copied, setCopied] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const activeCategories = useMemo(
    () => categories.filter((c) => c.active).map((c) => c.id),
    [categories]
  );

  const detectionSummary = useMemo(() => {
    const summary: Record<string, number> = {};
    detections.forEach((d) => {
      summary[d.type] = (summary[d.type] || 0) + 1;
    });
    return summary;
  }, [detections]);

  const handleFileUpload = useCallback(async (file: File) => {
    setError('');
    setLoading(true);
    try {
      const text = await uploadDocument(file);
      setInputText(text);
      setFileName(file.name);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to upload file';
      if (typeof err === 'object' && err !== null && 'response' in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setError(axiosErr.response?.data?.detail || msg);
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFileUpload(file);
    },
    [handleFileUpload]
  );

  const handleMask = useCallback(async () => {
    if (!inputText.trim()) {
      setError('Please enter or upload text to mask');
      return;
    }
    if (activeCategories.length === 0) {
      setError('Please select at least one PII category');
      return;
    }

    setError('');
    setLoading(true);
    setMaskedText('');
    setDetections([]);

    try {
      const result = await maskPII(inputText, activeCategories);
      setMaskedText(result.masked_text);
      setDetections(result.detections);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to mask PII';
      if (typeof err === 'object' && err !== null && 'response' in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setError(axiosErr.response?.data?.detail || msg);
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  }, [inputText, activeCategories]);

  const toggleCategory = useCallback((id: string) => {
    setCategories((prev) =>
      prev.map((c) => (c.id === id ? { ...c, active: !c.active } : c))
    );
  }, []);

  const addCustomCategory = useCallback(() => {
    const trimmed = customCategory.trim().toLowerCase();
    if (!trimmed || categories.some((c) => c.id === trimmed)) return;
    setCategories((prev) => [
      ...prev,
      { id: trimmed, label: customCategory.trim(), icon: '🏷️', active: true },
    ]);
    setCustomCategory('');
  }, [customCategory, categories]);

  const handleCopy = useCallback(async () => {
    await navigator.clipboard.writeText(maskedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [maskedText]);

  const removeFile = useCallback(() => {
    setFileName('');
    setInputText('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  }, []);

  // Render masked text with highlights
  const renderMaskedOutput = () => {
    if (!maskedText) return null;

    const parts: { text: string; isMasked: boolean }[] = [];
    let lastIdx = 0;

    // Find all ████ blocks in the masked text
    const maskPattern = /████/g;
    let match;
    while ((match = maskPattern.exec(maskedText)) !== null) {
      if (match.index > lastIdx) {
        parts.push({ text: maskedText.slice(lastIdx, match.index), isMasked: false });
      }
      parts.push({ text: '████', isMasked: true });
      lastIdx = match.index + match[0].length;
    }
    if (lastIdx < maskedText.length) {
      parts.push({ text: maskedText.slice(lastIdx), isMasked: false });
    }

    return parts.map((part, i) =>
      part.isMasked ? (
        <span key={i} className="masked-block">████</span>
      ) : (
        <span key={i}>{part.text}</span>
      )
    );
  };

  return (
    <>
      {/* Background effects */}
      <div className="grid-bg" />
      <div className="gradient-orb orb-1" />
      <div className="gradient-orb orb-2" />

      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-brand">
          <div className="navbar-logo">A</div>
          <div>
            <div className="navbar-title">Alta-Lex</div>
            <div className="navbar-subtitle">PII Shield</div>
          </div>
        </div>
        <div className="navbar-status">
          <span className="status-dot" />
          Qwen3-0.6B Online
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {/* Input Panel */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <span className="icon">&#9998;</span> Input
            </div>
          </div>
          <div className="panel-body">
            <textarea
              className="text-input"
              placeholder="Paste or type text containing PII here...&#10;&#10;Example: My name is John Smith, email john@example.com, phone 138-1234-5678"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />

            {/* File upload */}
            {fileName ? (
              <div className="file-info">
                <span className="file-name">📄 {fileName}</span>
                <button className="remove-btn" onClick={removeFile}>✕</button>
              </div>
            ) : (
              <div
                className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <div className="upload-icon">📁</div>
                <div className="upload-text">Drop a file here or click to upload</div>
                <div className="upload-formats">TXT, PDF, DOCX, CSV, XLSX</div>
              </div>
            )}
            <input
              ref={fileInputRef}
              type="file"
              hidden
              accept=".txt,.pdf,.docx,.csv,.xlsx"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleFileUpload(file);
              }}
            />

            {/* Categories */}
            <div className="categories-section">
              <div className="categories-header" onClick={() => setCategoriesOpen(!categoriesOpen)}>
                <span>🛡️ PII Categories ({activeCategories.length} active)</span>
                <span>{categoriesOpen ? '▾' : '▸'}</span>
              </div>
              {categoriesOpen && (
                <div className="categories-body">
                  {categories.map((cat) => (
                    <div
                      key={cat.id}
                      className={`category-tag ${cat.active ? 'active' : 'inactive'}`}
                      onClick={() => toggleCategory(cat.id)}
                    >
                      {cat.icon} {cat.label}
                    </div>
                  ))}
                  <div className="custom-category-input">
                    <input
                      placeholder="Add custom category..."
                      value={customCategory}
                      onChange={(e) => setCustomCategory(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && addCustomCategory()}
                    />
                    <button onClick={addCustomCategory}>+ Add</button>
                  </div>
                </div>
              )}
            </div>

            {error && <div className="error-message">⚠️ {error}</div>}

            <button
              className="btn-mask"
              onClick={handleMask}
              disabled={loading || !inputText.trim()}
            >
              {loading ? (
                <>
                  <span className="spinner" />
                  Analyzing...
                </>
              ) : (
                <>🛡️ Mask PII</>
              )}
            </button>
          </div>
        </div>

        {/* Output Panel */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <span className="icon">🔒</span> Masked Output
            </div>
            {maskedText && (
              <button className="btn-copy" onClick={handleCopy}>
                {copied ? '✓ Copied!' : '📋 Copy'}
              </button>
            )}
          </div>
          <div className="panel-body">
            {maskedText ? (
              <>
                <div className="output-text">{renderMaskedOutput()}</div>
                {detections.length > 0 && (
                  <div className="detection-summary">
                    {Object.entries(detectionSummary).map(([type, count]) => (
                      <div key={type} className="detection-badge">
                        {type}
                        <span className="count">{count}</span>
                      </div>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">🔍</div>
                <div className="empty-text">
                  Masked output will appear here
                </div>
                <div className="empty-text" style={{ fontSize: '0.75rem' }}>
                  Enter text and click "Mask PII" to start
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        Powered by <a href="https://www.alta-lex.ai/" target="_blank" rel="noopener noreferrer">Alta-Lex AI</a> &middot; PII Shield v1.0
      </footer>
    </>
  );
}

export default App;
