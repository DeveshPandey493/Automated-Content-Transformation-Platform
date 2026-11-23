"use client";

import { useState, useEffect } from "react";
import { Cpu, Zap, Cloud, HardDrive, CheckCircle, RefreshCw, Play, Sparkles } from "lucide-react";

interface ModelMetadata {
  model_id: string;
  name: string;
  family: string;
  provider: string;
  execution_type: string;
  supported_tasks: string[];
  is_available: boolean;
  description: string;
  resource_requirements: Record<string, any>;
}

export default function ModelLaboratoryPage() {
  const [models, setModels] = useState<ModelMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedModel, setSelectedModel] = useState<string>("extractive/textrank");
  const [promptText, setPromptText] = useState(
    "The Government of India has approved the National Quantum Mission (NQM) at a total cost of Rs. 6003.65 crore from 2023-24 to 2030-31. " +
    "The mission aims to seed, nurture and scale up scientific and industrial R&D and create a vibrant and innovative ecosystem in Quantum Technology (QT). " +
    "This will accelerate QT led economic growth, nurture the ecosystem in the country and make India one of the leading nations in the development of Quantum Technologies & Applications."
  );
  const [formatType, setFormatType] = useState("EXECUTIVE_SUMMARY");
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);

  const fetchModels = async () => {
    try {
      setLoading(true);
      const res = await fetch("/api/models");
      if (res.ok) {
        const data = await res.json();
        setModels(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const handleUnload = async (modelId: string) => {
    try {
      await fetch(`/api/models/${encodeURIComponent(modelId)}/unload`, { method: "POST" });
      fetchModels();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">AI Model Laboratory & Registry</h2>
        <p className="text-xs text-slate-400 mt-1">
          Inspect, compare, and manage generation engines across Extractive, Local Neural (FLAN-T5/BART), and Groq Cloud paradigms.
        </p>
      </div>

      {/* Model Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {loading ? (
          <div className="col-span-3 text-center py-12 text-xs text-slate-500">Loading model registry...</div>
        ) : (
          models.map((m) => {
            const isLocal = m.execution_type.includes("LOCAL");
            const isGroq = m.provider === "GROQ";
            return (
              <div
                key={m.model_id}
                className="p-5 rounded-xl bg-[#0f172a] border border-[#1e293b] flex flex-col justify-between space-y-4 hover:border-slate-700 transition-all"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                        isGroq
                          ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          : isLocal && m.family === "EXTRACTIVE"
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
                      }`}
                    >
                      {m.family}
                    </span>
                    <span className="flex items-center gap-1.5 text-[11px] text-emerald-400 font-medium">
                      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                      Available
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-white mb-1">{m.name}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">{m.description}</p>
                </div>

                <div className="space-y-3 pt-3 border-t border-[#1e293b]">
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span className="flex items-center gap-1.5">
                      {isGroq ? <Cloud className="w-3.5 h-3.5 text-amber-400" /> : <HardDrive className="w-3.5 h-3.5 text-sky-400" />}
                      Execution:
                    </span>
                    <span className="font-semibold text-slate-200">{m.execution_type}</span>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span>Provider:</span>
                    <span className="font-semibold text-slate-200">{m.provider}</span>
                  </div>

                  {m.family === "SEQ2SEQ" && (
                    <button
                      type="button"
                      onClick={() => handleUnload(m.model_id)}
                      className="w-full py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-medium border border-slate-700 transition-all flex items-center justify-center gap-1.5"
                    >
                      <RefreshCw className="w-3 h-3 text-slate-400" />
                      <span>Purge Model from VRAM</span>
                    </button>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Paradigm Architecture Comparison Card */}
      <div className="p-6 rounded-xl bg-[#0f172a] border border-[#1e293b] space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Zap className="w-4 h-4 text-sky-400" />
          <span>Paradigm Architectural Trade-Offs (SIH Research Framework)</span>
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="text-[11px] uppercase bg-[#090d16] text-slate-400 border-b border-[#1e293b]">
              <tr>
                <th className="py-2.5 px-4">Paradigm</th>
                <th className="py-2.5 px-4">Representative Model</th>
                <th className="py-2.5 px-4">Execution Mode</th>
                <th className="py-2.5 px-4">Hallucination Risk</th>
                <th className="py-2.5 px-4">Audience Adaptability</th>
                <th className="py-2.5 px-4">Typical Latency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e293b]">
              <tr>
                <td className="py-3 px-4 font-semibold text-emerald-400">Extractive Baseline</td>
                <td className="py-3 px-4">TextRank / TF-IDF Graph</td>
                <td className="py-3 px-4">100% Local CPU</td>
                <td className="py-3 px-4 font-semibold text-emerald-400">Zero (Verbatim)</td>
                <td className="py-3 px-4 text-slate-400">Low (Preserves original prose)</td>
                <td className="py-3 px-4 font-mono text-sky-400">~80 ms</td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-semibold text-indigo-400">Local Neural Seq2Seq</td>
                <td className="py-3 px-4">FLAN-T5-base / BART-base</td>
                <td className="py-3 px-4">RTX 4050 GPU (CUDA)</td>
                <td className="py-3 px-4 text-amber-400">Low to Moderate</td>
                <td className="py-3 px-4 text-slate-300">Moderate (Prefix prompt guided)</td>
                <td className="py-3 px-4 font-mono text-sky-400">~2.2 s</td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-semibold text-amber-400">Instruction-Tuned LLM</td>
                <td className="py-3 px-4">Groq LPU Engine</td>
                <td className="py-3 px-4">Cloud High-Throughput API</td>
                <td className="py-3 px-4 text-sky-400">Grounded (Mitigated by verifier)</td>
                <td className="py-3 px-4 font-semibold text-emerald-400">High (Audience & tone calibrated)</td>
                <td className="py-3 px-4 font-mono text-sky-400">~650 ms</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
