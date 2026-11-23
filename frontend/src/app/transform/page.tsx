"use client";

import { Suspense, useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Sparkles,
  Layers,
  Users,
  MessageSquare,
  Sliders,
  ShieldAlert,
  ArrowRight,
  Cpu,
  CheckCircle2,
  AlertCircle,
  FileText,
} from "lucide-react";

interface DocumentSummary {
  id: string;
  title: string;
  total_words: number;
}

interface ModelMetadata {
  model_id: string;
  name: string;
  family: string;
  provider: string;
  is_available: boolean;
}

const AUDIENCE_OPTIONS = [
  "Senior Management & Leadership",
  "General Citizens & Public",
  "Industry & Domain Professionals",
  "Technical & Engineering Experts",
  "Students & Academic Researchers",
];

const TONE_OPTIONS = [
  "Formal & Authoritative",
  "Clear & Direct (Plain Language)",
  "Conversational & Engaging",
  "Neutral & Analytical",
  "Persuasive & Action-Oriented",
];

function TransformationStudioContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialDocId = searchParams.get("doc_id") || "";

  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [models, setModels] = useState<ModelMetadata[]>([]);
  const [loadingInitial, setLoadingInitial] = useState(true);

  // Form State
  const [selectedDocId, setSelectedDocId] = useState(initialDocId);
  const [formatType, setFormatType] = useState<string>("EXECUTIVE_SUMMARY");
  const [audience, setAudience] = useState(AUDIENCE_OPTIONS[0]);
  const [tone, setTone] = useState(TONE_OPTIONS[0]);
  const [lengthTarget, setLengthTarget] = useState<string>("MEDIUM");
  const [customWords, setCustomWords] = useState<number>(300);
  const [requiredKeywords, setRequiredKeywords] = useState<string>("");
  const [prohibitedTerms, setProhibitedTerms] = useState<string>("");
  const [selectedModelIds, setSelectedModelIds] = useState<string[]>([]);

  const [generating, setGenerating] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/api/documents").then((r) => r.json()),
      fetch("/api/models").then((r) => r.json()),
    ])
      .then(([docsData, modelsData]) => {
        setDocuments(docsData);
        setModels(modelsData);
        if (selectedModelIds.length === 0 && Array.isArray(modelsData)) {
          const preferredModel = modelsData.find(
            (model: ModelMetadata) => model.is_available && model.family === "INSTRUCTION_LLM"
          );
          const baselineModel = modelsData.find(
            (model: ModelMetadata) => model.model_id === "extractive/textrank"
          );
          const initialModel = preferredModel || baselineModel || modelsData.find(
            (model: ModelMetadata) => model.is_available
          );
          if (initialModel) setSelectedModelIds([initialModel.model_id]);
        }
        if (!selectedDocId && docsData.length > 0) {
          setSelectedDocId(docsData[0].id);
        }
      })
      .catch((err) => console.error("Initialization error", err))
      .finally(() => setLoadingInitial(false));
  }, []);

  const handleToggleModel = (modelId: string) => {
    if (!models.find((model) => model.model_id === modelId)?.is_available) return;
    if (selectedModelIds.includes(modelId)) {
      if (selectedModelIds.length > 1) {
        setSelectedModelIds(selectedModelIds.filter((id) => id !== modelId));
      }
    } else {
      setSelectedModelIds([...selectedModelIds, modelId]);
    }
  };

  const handleStartTransformation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDocId) {
      setErrorMsg("Please select a source document.");
      return;
    }
    setGenerating(true);
    setErrorMsg(null);

    const kwList = requiredKeywords
      .split(",")
      .map((k) => k.trim())
      .filter((k) => k.length > 0);
    const ptList = prohibitedTerms
      .split(",")
      .map((p) => p.trim())
      .filter((p) => p.length > 0);

    try {
      const res = await fetch("/api/transformations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          document_id: selectedDocId,
          format_type: formatType,
          audience,
          tone,
          length_target: lengthTarget,
          custom_word_limit: lengthTarget === "CUSTOM" ? customWords : null,
          required_keywords: kwList,
          prohibited_terms: ptList,
          model_ids: selectedModelIds,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error?.message || "Transformation failed");
      }

      // Route to review page with the job id
      router.push(`/review?job_id=${data.id}`);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to trigger transformation");
      setGenerating(false);
    }
  };

  if (loadingInitial) {
    return <div className="text-center py-16 text-xs text-slate-500">Loading Transformation Studio...</div>;
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Transformation Studio</h2>
        <p className="text-xs text-slate-400 mt-1">
          Configure multi-audience synthesis with tone calibration, keyword preservation, and simultaneous model comparisons.
        </p>
      </div>

      {errorMsg && (
        <div className="flex items-center gap-2 p-3.5 bg-red-950/40 border border-red-500/30 rounded-xl text-xs text-red-300">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      <form onSubmit={handleStartTransformation} className="space-y-6">
        {/* Step 1: Source Document Selection */}
        <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6 space-y-4">
          <div className="flex items-center gap-2 text-xs font-bold text-sky-400 uppercase tracking-wider">
            <FileText className="w-4 h-4" />
            <span>1. Select Authoritative Source Document</span>
          </div>

          {documents.length === 0 ? (
            <div className="p-4 bg-[#090d16] rounded-lg border border-[#1e293b] text-xs text-slate-400">
              No documents available. Please upload a document in the{" "}
              <a href="/documents" className="text-sky-400 underline">
                Document Library
              </a>{" "}
              first.
            </div>
          ) : (
            <select
              value={selectedDocId}
              onChange={(e) => setSelectedDocId(e.target.value)}
              className="w-full bg-[#090d16] border border-[#1e293b] rounded-lg p-3 text-xs text-white focus:outline-none focus:border-sky-500"
            >
              {documents.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.title} ({d.total_words.toLocaleString()} words)
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Step 2: Format & Audience Calibration */}
        <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6 space-y-5">
          <div className="flex items-center gap-2 text-xs font-bold text-sky-400 uppercase tracking-wider">
            <Layers className="w-4 h-4" />
            <span>2. Target Communication Format</span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { id: "EXECUTIVE_SUMMARY", label: "Executive Summary", desc: "Briefing for senior leadership" },
              { id: "PUBLIC_ADVISORY", label: "Public Advisory", desc: "Citizen precautions & actions" },
              { id: "SOCIAL_POST", label: "Social Media Post", desc: "LinkedIn & X/Twitter posts" },
              { id: "FAQ", label: "FAQ Document", desc: "Citizen queries with evidence" },
            ].map((f) => (
              <button
                key={f.id}
                type="button"
                onClick={() => setFormatType(f.id)}
                className={`p-4 rounded-xl border text-left transition-all flex flex-col justify-between ${
                  formatType === f.id
                    ? "bg-sky-500/10 border-sky-500/40 text-white shadow-lg shadow-sky-500/10"
                    : "bg-[#090d16] border-[#1e293b] text-slate-400 hover:border-slate-700"
                }`}
              >
                <div>
                  <div className="text-xs font-bold text-white mb-1">{f.label}</div>
                  <div className="text-[11px] text-slate-400 leading-tight">{f.desc}</div>
                </div>
                {formatType === f.id && (
                  <div className="mt-3 text-[10px] font-semibold text-sky-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> Selected
                  </div>
                )}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5 text-sky-400" />
                Target Audience
              </label>
              <select
                value={audience}
                onChange={(e) => setAudience(e.target.value)}
                className="w-full bg-[#090d16] border border-[#1e293b] rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-sky-500"
              >
                {AUDIENCE_OPTIONS.map((a) => (
                  <option key={a} value={a}>
                    {a}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1.5">
                <MessageSquare className="w-3.5 h-3.5 text-indigo-400" />
                Tone Calibration
              </label>
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                className="w-full bg-[#090d16] border border-[#1e293b] rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-sky-500"
              >
                {TONE_OPTIONS.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Step 3: Controllability & Length Budget */}
        <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6 space-y-4">
          <div className="flex items-center gap-2 text-xs font-bold text-sky-400 uppercase tracking-wider">
            <Sliders className="w-4 h-4" />
            <span>3. Length Budget & Grounding Constraints</span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { id: "SHORT", label: "Short (~120w)", desc: "Quick briefing" },
              { id: "MEDIUM", label: "Medium (~250w)", desc: "Standard format" },
              { id: "DETAILED", label: "Detailed (~500w)", desc: "Comprehensive review" },
              { id: "CUSTOM", label: "Custom Word Limit", desc: "User defined budget" },
            ].map((l) => (
              <button
                key={l.id}
                type="button"
                onClick={() => setLengthTarget(l.id)}
                className={`p-3 rounded-lg border text-left transition-all ${
                  lengthTarget === l.id
                    ? "bg-sky-500/10 border-sky-500/40 text-white font-semibold"
                    : "bg-[#090d16] border-[#1e293b] text-slate-400"
                }`}
              >
                <div className="text-xs text-white">{l.label}</div>
                <div className="text-[10px] text-slate-400">{l.desc}</div>
              </button>
            ))}
          </div>

          {lengthTarget === "CUSTOM" && (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Custom Word Limit: {customWords} words
              </label>
              <input
                type="range"
                min="50"
                max="1000"
                step="25"
                value={customWords}
                onChange={(e) => setCustomWords(parseInt(e.target.value))}
                className="w-full"
              />
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Required Keywords (Comma-separated)
              </label>
              <input
                type="text"
                placeholder="e.g. fiscal deficit, 2030, renewable capacity"
                value={requiredKeywords}
                onChange={(e) => setRequiredKeywords(e.target.value)}
                className="w-full bg-[#090d16] border border-[#1e293b] rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1.5 text-amber-300">
                <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
                Prohibited Claims / Terms (Must avoid)
              </label>
              <input
                type="text"
                placeholder="e.g. unverified, rumored, unofficial"
                value={prohibitedTerms}
                onChange={(e) => setProhibitedTerms(e.target.value)}
                className="w-full bg-[#090d16] border border-[#1e293b] rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
              />
            </div>
          </div>
        </div>

        {/* Step 4: AI Model Selection (Supports 3-Way Multi-Model Comparison) */}
        <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-bold text-sky-400 uppercase tracking-wider">
              <Cpu className="w-4 h-4" />
              <span>4. Select AI Generation Engines (Multi-Model Comparison Supported)</span>
            </div>
            <span className="text-[11px] text-slate-400">
              Choose an available model. Groq is selected by default when configured; extractive is the offline baseline.
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {models.map((m) => {
              const isSelected = selectedModelIds.includes(m.model_id);
              return (
                <button
                  key={m.model_id}
                  type="button"
                  onClick={() => handleToggleModel(m.model_id)}
                  disabled={!m.is_available}
                  className={`p-4 rounded-xl border text-left transition-all flex items-center justify-between ${
                    isSelected
                      ? "bg-sky-500/10 border-sky-500/40 text-white"
                      : "bg-[#090d16] border-[#1e293b] text-slate-400 hover:border-slate-700"
                  }`}
                >
                  <div>
                    <div className="text-[10px] font-semibold text-sky-400 uppercase">{m.family}</div>
                    <div className="text-xs font-bold text-white mt-0.5">{m.name}</div>
                    <div className={`text-[10px] mt-1 ${m.is_available ? "text-emerald-400" : "text-amber-400"}`}>
                      {m.is_available ? (m.family === "EXTRACTIVE" ? "Available · source sentence extraction" : "Available · generated transformation") : "Unavailable · check provider setup"}
                    </div>
                  </div>
                  <div
                    className={`w-4 h-4 rounded border flex items-center justify-center ${
                      isSelected ? "bg-sky-500 border-sky-500 text-slate-950" : "border-slate-600"
                    }`}
                  >
                    {isSelected && <CheckCircle2 className="w-3.5 h-3.5" />}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={generating || !selectedDocId}
          className="w-full py-4 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-slate-950 font-bold text-sm shadow-xl shadow-sky-500/25 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {generating ? (
            <>
              <Sparkles className="w-4 h-4 animate-spin text-slate-950" />
              <span>Transforming Content & Verifying Factual Accuracy...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>
                Execute Transformation ({selectedModelIds.length}{" "}
                {selectedModelIds.length > 1 ? "Models" : "Model"})
              </span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>
    </div>
  );
}

export default function TransformationStudioPage() {
  return (
    <Suspense fallback={<div className="text-sm text-slate-400">Loading transformation studio…</div>}>
      <TransformationStudioContent />
    </Suspense>
  );
}
