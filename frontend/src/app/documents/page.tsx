"use client";

import { useState, useEffect } from "react";
import {
  Upload,
  FileText,
  Globe,
  Search,
  Plus,
  Layers,
  Calendar,
  Eye,
  CheckCircle2,
  AlertCircle,
  X,
  FileSpreadsheet,
} from "lucide-react";
import { formatBytes } from "@/lib/utils";

interface DocumentSummary {
  id: string;
  title: string;
  source_type: string;
  file_type?: string;
  file_size_bytes?: number;
  total_pages: number;
  total_characters: number;
  total_words: number;
  source_url?: string;
  created_at: string;
}

interface DocumentChunk {
  id: string;
  chunk_index: number;
  page_number?: number;
  section_heading?: string;
  char_start: number;
  char_end: number;
  text: string;
  token_count: number;
}

export default function DocumentLibraryPage() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [activeTab, setActiveTab] = useState<"upload" | "text" | "url">("upload");

  // Ingestion form state
  const [file, setFile] = useState<File | null>(null);
  const [docTitle, setDocTitle] = useState("");
  const [pastedText, setPastedText] = useState("");
  const [urlInput, setUrlInput] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Chunk inspection drawer
  const [selectedDoc, setSelectedDoc] = useState<DocumentSummary | null>(null);
  const [chunks, setChunks] = useState<DocumentChunk[]>([]);
  const [loadingChunks, setLoadingChunks] = useState(false);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const url = search ? `/api/documents?search=${encodeURIComponent(search)}` : "/api/documents";
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setDocuments(data);
      }
    } catch (err) {
      console.error("Failed to load documents", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [search]);

  const handleUploadFile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setSubmitting(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      if (docTitle) formData.append("title", docTitle);

      const res = await fetch("/api/documents/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error?.message || "Upload failed");
      }
      setSuccessMsg(`Document "${data.title}" successfully ingested!`);
      setFile(null);
      setDocTitle("");
      fetchDocuments();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to upload document");
    } finally {
      setSubmitting(false);
    }
  };

  const handleIngestText = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pastedText.trim() || !docTitle.trim()) return;
    setSubmitting(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      const res = await fetch("/api/documents/text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: docTitle, text: pastedText }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error?.message || "Failed to ingest text");
      }
      setSuccessMsg(`Document "${data.title}" successfully saved!`);
      setPastedText("");
      setDocTitle("");
      fetchDocuments();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to save text");
    } finally {
      setSubmitting(false);
    }
  };

  const handleIngestUrl = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!urlInput.trim()) return;
    setSubmitting(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      const res = await fetch("/api/documents/url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: urlInput, title: docTitle || undefined }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error?.message || "Failed to fetch URL");
      }
      setSuccessMsg(`Web document "${data.title}" successfully ingested!`);
      setUrlInput("");
      setDocTitle("");
      fetchDocuments();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to fetch URL");
    } finally {
      setSubmitting(false);
    }
  };

  const handleInspectChunks = async (doc: DocumentSummary) => {
    setSelectedDoc(doc);
    setLoadingChunks(true);
    try {
      const res = await fetch(`/api/documents/${doc.id}/chunks`);
      if (res.ok) {
        const data = await res.json();
        setChunks(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingChunks(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Document Library & Ingestion</h2>
        <p className="text-xs text-slate-400 mt-1">
          Upload authoritative source documents (PDF, DOCX, TXT) or ingest web advisories with traceable chunking.
        </p>
      </div>

      {/* Ingestion Panel */}
      <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6">
        {/* Tabs */}
        <div className="flex items-center gap-3 border-b border-[#1e293b] pb-4 mb-6">
          <button
            type="button"
            onClick={() => setActiveTab("upload")}
            className={`flex items-center gap-2 text-xs font-semibold px-4 py-2 rounded-lg transition-all ${
              activeTab === "upload"
                ? "bg-sky-500/10 text-sky-400 border border-sky-500/30"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Upload className="w-4 h-4" />
            <span>Upload Document (PDF / DOCX / TXT)</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("text")}
            className={`flex items-center gap-2 text-xs font-semibold px-4 py-2 rounded-lg transition-all ${
              activeTab === "text"
                ? "bg-sky-500/10 text-sky-400 border border-sky-500/30"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Paste Text</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("url")}
            className={`flex items-center gap-2 text-xs font-semibold px-4 py-2 rounded-lg transition-all ${
              activeTab === "url"
                ? "bg-sky-500/10 text-sky-400 border border-sky-500/30"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Globe className="w-4 h-4" />
            <span>Import from Web URL</span>
          </button>
        </div>

        {errorMsg && (
          <div className="mb-4 flex items-center gap-2 p-3 bg-red-950/40 border border-red-500/30 rounded-lg text-xs text-red-300">
            <AlertCircle className="w-4 h-4 text-red-400" />
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div className="mb-4 flex items-center gap-2 p-3 bg-emerald-950/40 border border-emerald-500/30 rounded-lg text-xs text-emerald-300">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>{successMsg}</span>
          </div>
        )}

        {activeTab === "upload" && (
          <form onSubmit={handleUploadFile} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Document Title (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Union Budget 2026 Fiscal Highlights"
                  value={docTitle}
                  onChange={(e) => setDocTitle(e.target.value)}
                  className="w-full bg-[#090d16] border border-[#1e293b] rounded-lg px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Select File (Max 25MB)
                </label>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="w-full bg-[#090d16] border border-[#1e293b] rounded-lg px-3 py-1.5 text-xs text-slate-300 file:mr-3 file:py-1 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-sky-500/10 file:text-sky-400"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={!file || submitting}
              className="bg-sky-500 hover:bg-sky-400 disabled:opacity-50 text-slate-950 font-semibold text-xs px-5 py-2 rounded-lg transition-all"
            >
              {submitting ? "Ingesting Document..." : "Upload & Process"}
            </button>
          </form>
        )}

        {activeTab === "text" && (
          <form onSubmit={handleIngestText} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Document Title
              </label>
              <input
                type="text"
                placeholder="e.g. National Green Hydrogen Policy Brief"
                value={docTitle}
                onChange={(e) => setDocTitle(e.target.value)}
                required
                className="w-full bg-[#090d16] border border-[#1e293b] rounded-lg px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Paste Source Text
              </label>
              <textarea
                rows={6}
                placeholder="Paste verbatim document text here..."
                value={pastedText}
                onChange={(e) => setPastedText(e.target.value)}
                required
                className="w-full bg-[#090d16] border border-[#1e293b] rounded-lg p-3.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 font-mono"
              />
            </div>
            <button
              type="submit"
              disabled={!pastedText.trim() || !docTitle.trim() || submitting}
              className="bg-sky-500 hover:bg-sky-400 disabled:opacity-50 text-slate-950 font-semibold text-xs px-5 py-2 rounded-lg transition-all"
            >
              {submitting ? "Segmenting Text..." : "Save & Segment"}
            </button>
          </form>
        )}

        {activeTab === "url" && (
          <form onSubmit={handleIngestUrl} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Web URL
                </label>
                <input
                  type="url"
                  placeholder="https://pib.gov.in/PressReleasePage.aspx?PRID=..."
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  required
                  className="w-full bg-[#090d16] border border-[#1e293b] rounded-lg px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Override Title (Optional)
                </label>
                <input
                  type="text"
                  placeholder="Title from article"
                  value={docTitle}
                  onChange={(e) => setDocTitle(e.target.value)}
                  className="w-full bg-[#090d16] border border-[#1e293b] rounded-lg px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
                />
              </div>
            </div>
            <p className="text-[11px] text-slate-500">
              🛡️ Protected by SSRF filtering. Loopback, private IP ranges (RFC 1918), and internal metadata endpoints are blocked.
            </p>
            <button
              type="submit"
              disabled={!urlInput.trim() || submitting}
              className="bg-sky-500 hover:bg-sky-400 disabled:opacity-50 text-slate-950 font-semibold text-xs px-5 py-2 rounded-lg transition-all"
            >
              {submitting ? "Fetching & Extracting..." : "Fetch Web Document"}
            </button>
          </form>
        )}
      </div>

      {/* Document Search & List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white">Ingested Documents ({documents.length})</h3>
          <div className="relative w-72">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search by document title..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-[#0f172a] border border-[#1e293b] rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
            />
          </div>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-slate-500">Loading documents...</div>
        ) : documents.length === 0 ? (
          <div className="p-12 text-center border border-dashed border-[#1e293b] rounded-xl bg-[#0f172a]/40">
            <FileText className="w-8 h-8 text-slate-600 mx-auto mb-2" />
            <p className="text-xs text-slate-400">No documents ingested yet.</p>
            <p className="text-[11px] text-slate-500 mt-1">Upload a PDF or paste text using the panel above.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="p-5 rounded-xl bg-[#0f172a] border border-[#1e293b] hover:border-slate-700 transition-all flex flex-col justify-between space-y-4"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
                      {doc.file_type || doc.source_type}
                    </span>
                    <span className="text-[11px] text-slate-500">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h4 className="text-sm font-semibold text-white line-clamp-2" title={doc.title}>
                    {doc.title}
                  </h4>
                </div>

                <div className="grid grid-cols-3 gap-2 pt-3 border-t border-[#1e293b] text-center">
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase">Words</div>
                    <div className="text-xs font-semibold text-slate-200">{doc.total_words.toLocaleString()}</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase">Pages</div>
                    <div className="text-xs font-semibold text-slate-200">{doc.total_pages}</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase">Size</div>
                    <div className="text-xs font-semibold text-slate-200">
                      {doc.file_size_bytes ? formatBytes(doc.file_size_bytes) : "Text"}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => handleInspectChunks(doc)}
                    className="flex-1 inline-flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-all"
                  >
                    <Eye className="w-3.5 h-3.5 text-sky-400" />
                    <span>Inspect Chunks</span>
                  </button>
                  <a
                    href={`/transform?doc_id=${doc.id}`}
                    className="flex-1 inline-flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 border border-sky-500/30 text-xs font-medium transition-all"
                  >
                    <Layers className="w-3.5 h-3.5" />
                    <span>Transform</span>
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Chunk Inspection Drawer */}
      {selectedDoc && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex justify-end">
          <div className="w-full max-w-2xl bg-[#0c1322] border-l border-[#1e293b] h-full flex flex-col p-6 overflow-hidden shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-[#1e293b]">
              <div>
                <span className="text-[11px] text-sky-400 font-semibold uppercase tracking-wider block">
                  Chunk Traceability Visualizer
                </span>
                <h3 className="text-sm font-bold text-white truncate max-w-md">{selectedDoc.title}</h3>
              </div>
              <button
                type="button"
                onClick={() => setSelectedDoc(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto py-4 space-y-3">
              {loadingChunks ? (
                <div className="text-xs text-slate-400 text-center py-12">Loading chunks...</div>
              ) : chunks.length === 0 ? (
                <div className="text-xs text-slate-400 text-center py-12">No chunks found for this document.</div>
              ) : (
                chunks.map((c) => (
                  <div
                    key={c.id}
                    className="p-4 rounded-lg bg-[#0f172a] border border-[#1e293b] space-y-2 text-xs"
                  >
                    <div className="flex items-center justify-between text-[11px] text-slate-400">
                      <span className="font-semibold text-sky-400">Chunk #{c.chunk_index}</span>
                      <div className="flex items-center gap-3">
                        {c.page_number && <span>Page {c.page_number}</span>}
                        {c.section_heading && <span>§ {c.section_heading}</span>}
                        <span>Chars: {c.char_start}–{c.char_end}</span>
                        <span>~{c.token_count} tokens</span>
                      </div>
                    </div>
                    <p className="text-slate-300 font-mono text-[11px] leading-relaxed bg-[#090d16] p-3 rounded border border-slate-800/80">
                      {c.text}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
