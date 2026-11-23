"use client";

import { useState, useEffect } from "react";
import {
  Database,
  FileText,
  RefreshCw,
  ChevronDown,
  ChevronRight,
  BookOpen,
  CheckCircle2,
  AlertCircle,
  Download,
  Plus,
  Search,
  Tag,
  BarChart3,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface DatasetDocument {
  id: string;
  source_title: string;
  source_organization: string;
  domain: string;
  extracted_text: string;
  gold_key_facts: string[];
  gold_entities: string[];
  gold_numbers: string[];
  reference_annotations: ReferenceAnnotation[];
}

interface ReferenceAnnotation {
  id: string;
  format_type: string;
  reference_text: string;
  annotator: string;
}

interface Dataset {
  id: string;
  name: string;
  version: string;
  description: string;
  total_documents: number;
  documents: DatasetDocument[];
  created_at: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedDoc, setExpandedDoc] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedDomain, setSelectedDomain] = useState("all");

  useEffect(() => {
    fetchDatasets();
  }, []);

  async function fetchDatasets() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/datasets`);
      if (!res.ok) throw new Error(`Failed: ${res.statusText}`);
      const data = await res.json();
      setDatasets(Array.isArray(data) ? data : [data]);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function seedDataset() {
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/api/datasets/seed`, { method: "POST" });
      if (!res.ok) throw new Error(`Seed failed: ${res.statusText}`);
      await fetchDatasets();
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  }

  // Gather all documents across datasets
  const allDocuments = datasets.flatMap((ds) => ds.documents || []);
  const domains = Array.from(new Set(allDocuments.map((d) => d.domain).filter(Boolean)));

  const filteredDocs = allDocuments.filter((doc) => {
    const matchesSearch =
      !searchQuery ||
      doc.source_title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.source_organization.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDomain = selectedDomain === "all" || doc.domain === selectedDomain;
    return matchesSearch && matchesDomain;
  });

  const totalFacts = allDocuments.reduce((s, d) => s + (d.gold_key_facts?.length || 0), 0);
  const totalAnnotations = allDocuments.reduce((s, d) => s + (d.reference_annotations?.length || 0), 0);

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Database className="w-7 h-7 text-sky-400" />
            Dataset Management
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Curated benchmark documents with gold-standard reference outputs for model evaluation
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={seedDataset}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-sky-600 hover:bg-sky-500 text-white transition-colors"
          >
            <Plus className="w-4 h-4" />
            Seed Benchmark
          </button>
          <button
            onClick={fetchDatasets}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
          >
            <RefreshCw className={cn("w-4 h-4", loading && "animate-spin")} />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Datasets", value: datasets.length, icon: Database, color: "sky" },
          { label: "Documents", value: allDocuments.length, icon: FileText, color: "indigo" },
          { label: "Gold Facts", value: totalFacts, icon: CheckCircle2, color: "emerald" },
          { label: "Reference Annotations", value: totalAnnotations, icon: BookOpen, color: "amber" },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-[#111827] border border-slate-800 rounded-xl p-5 flex items-center gap-4"
          >
            <div className={cn(
              "w-10 h-10 rounded-lg flex items-center justify-center",
              stat.color === "sky" && "bg-sky-500/10 text-sky-400",
              stat.color === "indigo" && "bg-indigo-500/10 text-indigo-400",
              stat.color === "emerald" && "bg-emerald-500/10 text-emerald-400",
              stat.color === "amber" && "bg-amber-500/10 text-amber-400",
            )}>
              <stat.icon className="w-5 h-5" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{stat.value}</p>
              <p className="text-xs text-slate-400">{stat.label}</p>
            </div>
          </div>
        ))}
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <p className="text-sm text-red-300">{error}</p>
        </div>
      )}

      {/* Filter Bar */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-sky-500"
          />
        </div>
        <select
          value={selectedDomain}
          onChange={(e) => setSelectedDomain(e.target.value)}
          className="px-3 py-2.5 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-sky-500"
        >
          <option value="all">All Domains</option>
          {domains.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
      </div>

      {/* Dataset Info Card */}
      {datasets.map((ds) => (
        <div key={ds.id} className="bg-[#111827] border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-5 border-b border-slate-800 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-white">{ds.name}</h2>
              <p className="text-sm text-slate-400 mt-0.5">{ds.description}</p>
            </div>
            <div className="flex items-center gap-3">
              <span className="px-2.5 py-1 rounded-full bg-sky-500/10 text-sky-400 text-xs font-medium border border-sky-500/20">
                v{ds.version}
              </span>
              <span className="text-xs text-slate-500">
                {ds.total_documents} documents
              </span>
            </div>
          </div>
        </div>
      ))}

      {/* Document List */}
      <div className="space-y-3">
        {loading && allDocuments.length === 0 ? (
          <div className="text-center py-12">
            <RefreshCw className="w-8 h-8 text-slate-500 animate-spin mx-auto mb-3" />
            <p className="text-sm text-slate-400">Loading datasets...</p>
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="text-center py-12">
            <Database className="w-8 h-8 text-slate-500 mx-auto mb-3" />
            <p className="text-sm text-slate-400">No benchmark documents found.</p>
            <button
              onClick={seedDataset}
              className="mt-3 px-4 py-2 rounded-lg text-sm font-medium bg-sky-600 hover:bg-sky-500 text-white transition-colors"
            >
              Seed Benchmark Dataset
            </button>
          </div>
        ) : (
          filteredDocs.map((doc) => {
            const isExpanded = expandedDoc === doc.id;
            return (
              <div
                key={doc.id}
                className="bg-[#111827] border border-slate-800 rounded-xl overflow-hidden"
              >
                {/* Doc Header */}
                <button
                  onClick={() => setExpandedDoc(isExpanded ? null : doc.id)}
                  className="w-full p-5 flex items-center justify-between text-left hover:bg-slate-800/30 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <FileText className="w-5 h-5 text-indigo-400 shrink-0" />
                    <div>
                      <h3 className="text-sm font-semibold text-white">{doc.source_title}</h3>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {doc.source_organization} · <span className="text-sky-400">{doc.domain}</span>
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-3 text-xs text-slate-400">
                      <span className="flex items-center gap-1">
                        <Tag className="w-3 h-3" />
                        {doc.gold_key_facts?.length || 0} facts
                      </span>
                      <span className="flex items-center gap-1">
                        <BarChart3 className="w-3 h-3" />
                        {doc.reference_annotations?.length || 0} refs
                      </span>
                    </div>
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-slate-500" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-slate-500" />
                    )}
                  </div>
                </button>

                {/* Expanded Detail */}
                {isExpanded && (
                  <div className="border-t border-slate-800 p-5 space-y-5">
                    {/* Source Text Preview */}
                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                        Source Text Preview
                      </h4>
                      <div className="bg-slate-900/60 rounded-lg p-4 text-xs text-slate-300 max-h-40 overflow-y-auto font-mono leading-relaxed">
                        {doc.extracted_text?.slice(0, 800) || "No text available"}
                        {(doc.extracted_text?.length || 0) > 800 && "..."}
                      </div>
                    </div>

                    {/* Gold Key Facts */}
                    {doc.gold_key_facts && doc.gold_key_facts.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                          Gold Key Facts ({doc.gold_key_facts.length})
                        </h4>
                        <div className="space-y-1.5">
                          {doc.gold_key_facts.map((fact, idx) => (
                            <div
                              key={idx}
                              className="flex items-start gap-2 text-xs text-slate-300 bg-emerald-500/5 border border-emerald-500/10 rounded-lg px-3 py-2"
                            >
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                              <span>{fact}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Gold Entities & Numbers */}
                    <div className="grid grid-cols-2 gap-4">
                      {doc.gold_entities && doc.gold_entities.length > 0 && (
                        <div>
                          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                            Gold Entities
                          </h4>
                          <div className="flex flex-wrap gap-1.5">
                            {doc.gold_entities.map((e, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-1 rounded-md bg-indigo-500/10 text-indigo-300 text-xs border border-indigo-500/20"
                              >
                                {e}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {doc.gold_numbers && doc.gold_numbers.length > 0 && (
                        <div>
                          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                            Gold Numbers
                          </h4>
                          <div className="flex flex-wrap gap-1.5">
                            {doc.gold_numbers.map((n, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-1 rounded-md bg-amber-500/10 text-amber-300 text-xs border border-amber-500/20"
                              >
                                {n}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Reference Annotations */}
                    {doc.reference_annotations && doc.reference_annotations.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                          Reference Outputs ({doc.reference_annotations.length})
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {doc.reference_annotations.map((ref) => (
                            <div
                              key={ref.id}
                              className="bg-slate-900/60 rounded-lg p-4 border border-slate-700/50"
                            >
                              <div className="flex items-center justify-between mb-2">
                                <span className="px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 text-xs font-medium">
                                  {ref.format_type.replace(/_/g, " ")}
                                </span>
                                <span className="text-[10px] text-slate-500">
                                  by {ref.annotator}
                                </span>
                              </div>
                              <p className="text-xs text-slate-300 max-h-24 overflow-y-auto leading-relaxed">
                                {ref.reference_text?.slice(0, 400) || "—"}
                                {(ref.reference_text?.length || 0) > 400 && "..."}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
