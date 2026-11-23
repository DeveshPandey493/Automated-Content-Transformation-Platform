"use client";

import { Suspense, useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  ShieldCheck,
  FileText,
  Download,
  Edit3,
  Save,
  Star,
  Layers,
  Clock,
  Sparkles,
  ExternalLink,
  Cpu,
} from "lucide-react";

interface EvidenceRef {
  id: string;
  chunk_id: string;
  relevance_score: number;
  evidence_text: string;
}

interface Claim {
  id: string;
  claim_text: string;
  claim_type: string;
  verification_status: "SUPPORTED" | "PARTIALLY_SUPPORTED" | "UNSUPPORTED" | "CONTRADICTED" | "REQUIRES_HUMAN_REVIEW";
  confidence_score: number;
  explanation?: string;
  evidence_references: EvidenceRef[];
}

interface VerificationReport {
  total_claims: number;
  supported_claims: number;
  partially_supported: number;
  unsupported_claims: number;
  contradicted_claims: number;
  factual_consistency_score: number;
  summary?: string;
  claims: Claim[];
}

interface GeneratedOutput {
  id: string;
  model_id: string;
  model_provider: string;
  content: string;
  word_count: number;
  generation_latency_ms: number;
  input_tokens: number;
  output_tokens: number;
  estimated_cost_usd: number;
  verification_report?: VerificationReport;
  generation_params: Record<string, any>;
}

interface TransformationJob {
  id: string;
  document_id: string;
  format_type: string;
  audience: string;
  tone: string;
  status: string;
  error_message?: string | null;
  outputs: GeneratedOutput[];
}

function ReviewTraceabilityContent() {
  const searchParams = useSearchParams();
  const jobId = searchParams.get("job_id");

  const [jobs, setJobs] = useState<TransformationJob[]>([]);
  const [selectedJob, setSelectedJob] = useState<TransformationJob | null>(null);
  const [selectedOutputIndex, setSelectedOutputIndex] = useState<number>(0);
  const [activeClaim, setActiveClaim] = useState<Claim | null>(null);

  // Edit output state
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState("");

  // Human feedback state
  const [ratingAccuracy, setRatingAccuracy] = useState(5);
  const [ratingCompleteness, setRatingCompleteness] = useState(5);
  const [ratingReadability, setRatingReadability] = useState(5);
  const [ratingSuitability, setRatingSuitability] = useState(5);
  const [feedbackSaved, setFeedbackSaved] = useState(false);

  useEffect(() => {
    fetch("/api/transformations")
      .then((r) => r.json())
      .then((data: TransformationJob[]) => {
        setJobs(data);
        if (data.length > 0) {
          const match = jobId ? data.find((j) => j.id === jobId) || data[0] : data[0];
          setSelectedJob(match);
          if (match.outputs.length > 0) {
            setEditedContent(match.outputs[0].content);
            fetchFullVerification(match.outputs[0].id);
          }
        }
      })
      .catch((err) => console.error(err));
  }, [jobId]);

  const fetchFullVerification = async (outputId: string) => {
    try {
      const res = await fetch(`/api/verification/${outputId}`);
      if (res.ok) {
        const report = await res.json();
        setSelectedJob((prev) => {
          if (!prev) return prev;
          const updatedOutputs = prev.outputs.map((out) =>
            out.id === outputId ? { ...out, verification_report: report } : out
          );
          return { ...prev, outputs: updatedOutputs };
        });
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSelectOutput = (idx: number) => {
    setSelectedOutputIndex(idx);
    setActiveClaim(null);
    setIsEditing(false);
    if (selectedJob && selectedJob.outputs[idx]) {
      setEditedContent(selectedJob.outputs[idx].content);
      fetchFullVerification(selectedJob.outputs[idx].id);
    }
  };

  const currentOutput = selectedJob?.outputs[selectedOutputIndex];
  const report = currentOutput?.verification_report;

  const handleExport = (format: "pdf" | "docx" | "md" | "txt") => {
    if (!currentOutput) return;
    window.open(`/api/exports/${currentOutput.id}?format=${format}`, "_blank");
  };

  const handleSaveFeedback = async () => {
    if (!currentOutput) return;
    try {
      await fetch("/api/evaluations/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          output_id: currentOutput.id,
          rating_accuracy: ratingAccuracy,
          rating_completeness: ratingCompleteness,
          rating_readability: ratingReadability,
          rating_suitability: ratingSuitability,
        }),
      });
      setFeedbackSaved(true);
      setTimeout(() => setFeedbackSaved(false), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  if (!selectedJob || !currentOutput) {
    return (
      <div className="max-w-4xl mx-auto py-16 text-center space-y-3">
        <FileText className="w-10 h-10 text-slate-600 mx-auto" />
        <h3 className="text-base font-semibold text-white">No Transformed Outputs Available</h3>
        <p className="text-xs text-slate-400">Run a transformation from the Transformation Studio first.</p>
        <a
          href="/transform"
          className="inline-flex items-center gap-2 mt-2 px-4 py-2 bg-sky-500 text-slate-950 font-bold text-xs rounded-lg"
        >
          <span>Open Transformation Studio</span>
        </a>
      </div>
    );
  }

  const fcsPercent = report ? Math.round(report.factual_consistency_score * 100) : 100;

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Top Bar with Job & Output Switcher */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0f172a] border border-[#1e293b] p-5 rounded-xl">
        <div>
          <div className="flex items-center gap-2 text-[11px] text-sky-400 font-semibold uppercase tracking-wider mb-1">
            <span>{selectedJob.format_type.replace("_", " ")}</span>
            <span>·</span>
            <span>Audience: {selectedJob.audience}</span>
          </div>
          <h2 className="text-lg font-bold text-white tracking-tight">Results & Factual Verification Review</h2>
        </div>

        {/* Multi-Model Tabs */}
        <div className="flex items-center gap-2 overflow-x-auto">
          {selectedJob.outputs.map((out, idx) => (
            <button
              key={out.id}
              type="button"
              onClick={() => handleSelectOutput(idx)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                selectedOutputIndex === idx
                  ? "bg-sky-500 text-slate-950 shadow-md shadow-sky-500/20"
                  : "bg-[#090d16] text-slate-400 border border-[#1e293b] hover:text-white"
              }`}
            >
              <Cpu className="w-3.5 h-3.5" />
              <span>{out.model_id.replace("extractive/", "").replace("seq2seq/", "")}</span>
            </button>
          ))}
        </div>
      </div>

      {selectedJob.error_message && (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-xs text-amber-200">
          <div className="font-semibold mb-1">
            {selectedJob.status === "COMPLETED" ? "Some selected models did not generate an output" : "Transformation failed"}
          </div>
          <p className="whitespace-pre-wrap break-words">{selectedJob.error_message}</p>
          <p className="mt-2 text-amber-100/70">
            The displayed output is from {currentOutput.model_id}. Extractive results quote source sentences; choose an available instruction or sequence model for rewritten content.
          </p>
        </div>
      )}

      {/* Main Grid: Output Content vs Verification Audit */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Generated Text / Editor (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6 flex flex-col h-[750px]">
            {/* Header Toolbar */}
            <div className="flex items-center justify-between pb-4 border-b border-[#1e293b] mb-4">
              <div className="flex items-center gap-4 text-xs text-slate-400">
                <span>
                  Words: <strong className="text-white">{currentOutput.word_count}</strong>
                </span>
                <span>
                  Latency: <strong className="text-sky-400">{currentOutput.generation_latency_ms} ms</strong>
                </span>
                {currentOutput.output_tokens > 0 && (
                  <span>
                    Tokens: <strong className="text-slate-300">{currentOutput.output_tokens}</strong>
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setIsEditing(!isEditing)}
                  className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-[11px] text-slate-300 flex items-center gap-1 border border-slate-700"
                >
                  <Edit3 className="w-3 h-3" />
                  <span>{isEditing ? "View" : "Edit"}</span>
                </button>

                <div className="relative group">
                  <button
                    type="button"
                    className="px-2.5 py-1 rounded bg-sky-500/10 hover:bg-sky-500/20 text-[11px] text-sky-400 border border-sky-500/30 flex items-center gap-1 font-medium"
                  >
                    <Download className="w-3 h-3" />
                    <span>Export</span>
                  </button>
                  <div className="hidden group-hover:flex flex-col absolute right-0 top-full mt-1 w-32 bg-[#0c1322] border border-[#1e293b] rounded-lg shadow-xl z-30 p-1">
                    <button
                      onClick={() => handleExport("pdf")}
                      className="text-left px-2.5 py-1.5 text-xs text-slate-300 hover:bg-slate-800 rounded"
                    >
                      Export PDF
                    </button>
                    <button
                      onClick={() => handleExport("docx")}
                      className="text-left px-2.5 py-1.5 text-xs text-slate-300 hover:bg-slate-800 rounded"
                    >
                      Export DOCX
                    </button>
                    <button
                      onClick={() => handleExport("md")}
                      className="text-left px-2.5 py-1.5 text-xs text-slate-300 hover:bg-slate-800 rounded"
                    >
                      Export Markdown
                    </button>
                    <button
                      onClick={() => handleExport("txt")}
                      className="text-left px-2.5 py-1.5 text-xs text-slate-300 hover:bg-slate-800 rounded"
                    >
                      Export TXT
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Content Display / Editor */}
            <div className="flex-1 overflow-y-auto pr-2">
              {isEditing ? (
                <textarea
                  value={editedContent}
                  onChange={(e) => setEditedContent(e.target.value)}
                  className="w-full h-full bg-[#090d16] border border-[#1e293b] rounded-lg p-4 text-xs text-slate-200 font-mono focus:outline-none focus:border-sky-500 resize-none leading-relaxed"
                />
              ) : (
                <div className="prose prose-invert max-w-none text-xs text-slate-200 leading-relaxed space-y-3 font-sans">
                  {currentOutput.content.split("\n\n").map((para, i) => (
                    <p key={i} className="whitespace-pre-wrap">
                      {para}
                    </p>
                  ))}
                </div>
              )}
            </div>

            {/* Human Evaluation Bar */}
            <div className="pt-4 border-t border-[#1e293b] mt-4 flex items-center justify-between text-xs">
              <span className="text-slate-400 font-medium">Rate Quality (1-5★):</span>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1">
                  <span className="text-[11px] text-slate-500">Acc:</span>
                  {[1, 2, 3, 4, 5].map((s) => (
                    <button
                      key={s}
                      onClick={() => setRatingAccuracy(s)}
                      className={`w-4 h-4 ${s <= ratingAccuracy ? "text-amber-400" : "text-slate-600"}`}
                    >
                      ★
                    </button>
                  ))}
                </div>
                <div className="flex items-center gap-1">
                  <span className="text-[11px] text-slate-500">Read:</span>
                  {[1, 2, 3, 4, 5].map((s) => (
                    <button
                      key={s}
                      onClick={() => setRatingReadability(s)}
                      className={`w-4 h-4 ${s <= ratingReadability ? "text-amber-400" : "text-slate-600"}`}
                    >
                      ★
                    </button>
                  ))}
                </div>
                <button
                  type="button"
                  onClick={handleSaveFeedback}
                  className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-semibold"
                >
                  {feedbackSaved ? "Saved!" : "Save Rating"}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Factual Verification & Traceability Drawer (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Factuality Scorecard */}
          <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <h3 className="text-sm font-bold text-white">Factual Consistency Audit</h3>
              </div>
              <div className="text-right">
                <div className="text-lg font-black text-emerald-400">{fcsPercent}%</div>
                <div className="text-[10px] text-slate-400 uppercase tracking-wider">Consistency Score</div>
              </div>
            </div>

            {report && (
              <div className="grid grid-cols-4 gap-2 text-center pt-2 border-t border-[#1e293b]">
                <div className="p-2 rounded bg-emerald-500/10 border border-emerald-500/20">
                  <div className="text-xs font-bold text-emerald-400">{report.supported_claims}</div>
                  <div className="text-[9px] text-emerald-300/80 uppercase">Supported</div>
                </div>
                <div className="p-2 rounded bg-amber-500/10 border border-amber-500/20">
                  <div className="text-xs font-bold text-amber-400">{report.partially_supported}</div>
                  <div className="text-[9px] text-amber-300/80 uppercase">Partial</div>
                </div>
                <div className="p-2 rounded bg-orange-500/10 border border-orange-500/20">
                  <div className="text-xs font-bold text-orange-400">{report.unsupported_claims}</div>
                  <div className="text-[9px] text-orange-300/80 uppercase">Unproven</div>
                </div>
                <div className="p-2 rounded bg-red-500/10 border border-red-500/20">
                  <div className="text-xs font-bold text-red-400">{report.contradicted_claims}</div>
                  <div className="text-[9px] text-red-300/80 uppercase">Conflict</div>
                </div>
              </div>
            )}
          </div>

          {/* Atomic Claims List */}
          <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-5 flex flex-col h-[520px]">
            <div className="flex items-center justify-between pb-3 border-b border-[#1e293b] mb-3">
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                Extracted Claims ({report?.claims.length || 0})
              </h4>
              <span className="text-[10px] text-slate-400">Click a claim to inspect source evidence</span>
            </div>

            <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
              {!report || report.claims.length === 0 ? (
                <div className="text-xs text-slate-500 text-center py-12">No claims extracted yet.</div>
              ) : (
                report.claims.map((claim) => {
                  const isSelected = activeClaim?.id === claim.id;
                  let badgeColor = "bg-slate-800 text-slate-300 border-slate-700";
                  let Icon = HelpCircle;

                  if (claim.verification_status === "SUPPORTED") {
                    badgeColor = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
                    Icon = CheckCircle2;
                  } else if (claim.verification_status === "PARTIALLY_SUPPORTED") {
                    badgeColor = "bg-amber-500/10 text-amber-400 border-amber-500/30";
                    Icon = AlertTriangle;
                  } else if (claim.verification_status === "CONTRADICTED") {
                    badgeColor = "bg-red-500/10 text-red-400 border-red-500/30";
                    Icon = XCircle;
                  } else if (claim.verification_status === "UNSUPPORTED") {
                    badgeColor = "bg-orange-500/10 text-orange-400 border-orange-500/30";
                    Icon = AlertTriangle;
                  }

                  return (
                    <div
                      key={claim.id}
                      onClick={() => setActiveClaim(claim)}
                      className={`p-3 rounded-lg border cursor-pointer transition-all ${
                        isSelected
                          ? "bg-slate-800/80 border-sky-500 ring-1 ring-sky-500/30"
                          : "bg-[#090d16] border-[#1e293b] hover:border-slate-700"
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2 mb-1.5">
                        <span
                          className={`text-[9px] font-bold px-1.5 py-0.5 rounded border uppercase flex items-center gap-1 ${badgeColor}`}
                        >
                          <Icon className="w-2.5 h-2.5" />
                          <span>{claim.verification_status.replace("_", " ")}</span>
                        </span>
                        <span className="text-[10px] text-slate-400 font-mono">
                          Conf: {Math.round(claim.confidence_score * 100)}%
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-200 line-clamp-2">{claim.claim_text}</p>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Active Claim Source Evidence Drawer */}
          {activeClaim && (
            <div className="p-4 rounded-xl bg-gradient-to-tr from-sky-950/40 to-slate-900 border border-sky-500/30 space-y-2 text-xs">
              <div className="flex items-center justify-between text-sky-400 font-bold text-[11px]">
                <span>Source Document Traceability</span>
                <span className="uppercase text-[9px] font-bold bg-sky-500/20 px-1.5 py-0.5 rounded">
                  {activeClaim.claim_type}
                </span>
              </div>
              <p className="text-slate-300 text-[11px] italic bg-[#090d16]/80 p-2.5 rounded border border-slate-800">
                "{activeClaim.claim_text}"
              </p>
              <div className="text-[11px] text-slate-400 pt-1">
                <strong className="text-white">Verifier Rationale:</strong> {activeClaim.explanation}
              </div>
              {activeClaim.evidence_references.length > 0 && (
                <div className="pt-2 border-t border-[#1e293b]">
                  <div className="text-[10px] uppercase font-bold text-slate-400 mb-1">
                    Supporting Source Chunk:
                  </div>
                  <div className="p-2.5 rounded bg-[#090d16] border border-[#1e293b] font-mono text-[10px] text-slate-300">
                    {activeClaim.evidence_references[0].evidence_text}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ReviewTraceabilityPage() {
  return (
    <Suspense fallback={<div className="text-sm text-slate-400">Loading review workspace…</div>}>
      <ReviewTraceabilityContent />
    </Suspense>
  );
}
