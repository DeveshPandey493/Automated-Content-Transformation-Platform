"use client";

import { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
} from "recharts";
import {
  BarChart3,
  TrendingUp,
  Download,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  XCircle,
  Sparkles,
  Filter,
  ChevronDown,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface EvaluationRow {
  model_id: string;
  model_name: string;
  provider: string;
  content: string;
  word_count: number;
  latency_ms: number;
  factual_consistency_score: number;
  supported_claims: number;
  total_claims: number;
  rouge_1_f1: number;
  rouge_2_f1: number;
  rouge_l_f1: number;
  controllability_score: number;
  estimated_cost_usd: number;
}

interface ComparisonResponse {
  document_id: string;
  document_title: string;
  format_type: string;
  rows: EvaluationRow[];
}

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

const PROVIDER_COLORS: Record<string, string> = {
  LOCAL_EXTRACTIVE: "#10b981",
  LOCAL_SEQ2SEQ: "#6366f1",
  GROQ: "#f59e0b",
};

const RADAR_INDICATORS = [
  { key: "factual_consistency_score", label: "Factual Consistency", max: 1 },
  { key: "rouge_1_f1", label: "ROUGE-1 F1", max: 1 },
  { key: "rouge_l_f1", label: "ROUGE-L F1", max: 1 },
  { key: "controllability_score", label: "Controllability", max: 1 },
];

export default function EvaluationDashboardPage() {
  const [comparisons, setComparisons] = useState<ComparisonResponse[]>([]);
  const [models, setModels] = useState<ModelMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFormat, setSelectedFormat] = useState<string>("ALL");
  const [viewMode, setViewMode] = useState<"radar" | "bars" | "table">("radar");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchModels();
    fetchComparisons();
  }, []);

  const fetchModels = async () => {
    try {
      const res = await fetch("/api/models");
      if (res.ok) {
        const data = await res.json();
        setModels(data);
      }
    } catch (err) {
      console.error("Failed to load models", err);
    }
  };

  const fetchComparisons = async () => {
    try {
      setLoading(true);
      const res = await fetch("/api/evaluations/compare-all");
      if (res.ok) {
        const data = await res.json();
        setComparisons(data);
      } else {
        setError("Failed to load evaluation comparisons");
      }
    } catch (err) {
      console.error("Failed to load comparisons", err);
      setError("Error loading evaluation data");
    } finally {
      setLoading(false);
    }
  };

  const getAllRows = (): (EvaluationRow & { document_title: string; format_type: string })[] => {
    const allRows: (EvaluationRow & { document_title: string; format_type: string })[] = [];
    comparisons.forEach((comp) => {
      comp.rows.forEach((row) => {
        allRows.push({ ...row, document_title: comp.document_title, format_type: comp.format_type });
      });
    });
    return allRows;
  };

  const filteredRows = getAllRows().filter((r) => selectedFormat === "ALL" || r.format_type === selectedFormat);

  const formatTypes = Array.from(new Set(comparisons.map((comparison) => comparison.format_type)));

  const getModelColor = (modelId: string) => {
    const model = models.find((m) => m.model_id === modelId);
    if (model) return PROVIDER_COLORS[model.provider] || "#64748b";
    if (modelId.includes("extractive")) return PROVIDER_COLORS.LOCAL_EXTRACTIVE;
    if (modelId.includes("seq2seq")) return PROVIDER_COLORS.LOCAL_SEQ2SEQ;
    if (modelId.includes("groq")) return PROVIDER_COLORS.GROQ;
    return "#64748b";
  };

  const radarData = RADAR_INDICATORS.map((indicator) => ({
    metric: indicator.label,
    ...Object.fromEntries(
      filteredRows.map((row) => [
        row.model_id,
        Math.round(Number(row[indicator.key as keyof EvaluationRow]) * 100),
      ])
    ),
  }));

  const barChartData = filteredRows.map((row) => ({
    name: row.model_name.replace("Local Seq2Seq (", "").replace("Groq (", "").replace("Extractive Baseline (", "").replace(")", ""),
    "Factual Consistency": Math.round(row.factual_consistency_score * 100),
    "ROUGE-1": Math.round(row.rouge_1_f1 * 100),
    "ROUGE-L": Math.round(row.rouge_l_f1 * 100),
    Controllability: Math.round(row.controllability_score * 100),
    Latency: Math.min(100, Math.round(100 - row.latency_ms / 50)), // normalized inverse
    Cost: row.estimated_cost_usd > 0 ? Math.round(100 - Math.min(100, row.estimated_cost_usd * 1000)) : 100,
    color: getModelColor(row.model_id),
  }));

  const latencyData = filteredRows.map((row) => ({
    name: row.model_name.replace("Local Seq2Seq (", "").replace("Groq (", "").replace("Extractive Baseline (", "").replace(")", ""),
    Latency: row.latency_ms,
    color: getModelColor(row.model_id),
  }));

  const costData = filteredRows
    .filter((r) => r.estimated_cost_usd > 0)
    .map((row) => ({
      name: row.model_name.replace("Local Seq2Seq (", "").replace("Groq (", "").replace("Extractive Baseline (", "").replace(")", ""),
      Cost: row.estimated_cost_usd * 1000000, // micro-dollars for readability
      color: getModelColor(row.model_id),
    }));

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Evaluation Dashboard</h2>
            <p className="text-xs text-slate-400 mt-1">Multi-model comparative benchmarking across 5 evaluation dimensions</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="p-5 rounded-xl bg-[#0f172a] border border-[#1e293b] animate-pulse">
              <div className="h-4 bg-slate-700 rounded w-3/4 mb-2" />
              <div className="h-8 bg-slate-700 rounded w-1/2" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Evaluation Dashboard</h2>
          <p className="text-xs text-slate-400 mt-1">
            Compare Extractive, Seq2Seq (FLAN-T5/BART), and Groq LLMs across Factual Consistency, ROUGE, Controllability, Latency & Cost
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <select
              value={selectedFormat}
              onChange={(e) => setSelectedFormat(e.target.value)}
              className="bg-[#0f172a] border border-[#1e293b] rounded-lg px-3.5 py-2 text-xs text-white focus:outline-none focus:border-sky-500 appearance-none pr-8"
            >
              <option value="ALL">All Formats</option>
              {formatTypes.map((fmt) => (
                <option key={fmt} value={fmt}>
                  {fmt.replace("_", " ")}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
          </div>
          <button
            onClick={fetchComparisons}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-medium border border-slate-700 transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3.5 bg-red-950/40 border border-red-500/30 rounded-xl text-xs text-red-300">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* View Mode Tabs */}
      <div className="flex items-center gap-2 bg-[#0f172a] border border-[#1e293b] rounded-xl p-1">
        {[
          { id: "radar", label: "Radar Chart", icon: Sparkles },
          { id: "bars", label: "Bar Charts", icon: BarChart3 },
          { id: "table", label: "Detailed Table", icon: TrendingUp },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setViewMode(tab.id as "radar" | "bars" | "table")}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all",
                viewMode === tab.id
                  ? "bg-sky-500 text-slate-950 shadow-md"
                  : "text-slate-400 hover:text-white"
              )}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {viewMode === "radar" && (
        <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6">
          <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-sky-400" />
            Multi-Dimensional Radar Comparison
          </h3>
          <p className="text-xs text-slate-400 mb-4">
            Normalized scores (0-100) across 5 evaluation dimensions. Higher is better for all metrics.
            Cost & Latency are inverted (100 = lowest cost/latency).
          </p>
          <div className="h-[450px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart
                cx="50%"
                cy="50%"
                outerRadius="45%"
                data={radarData.length > 0 ? radarData : [{ metric: "No Data" }]}
              >
                <PolarGrid gridType="polygon" stroke="#1e293b" />
                <PolarAngleAxis dataKey="metric" stroke="#1e293b" tick={{ fill: "#64748b", fontSize: 11 }} />
                <PolarRadiusAxis
                  angle={90}
                  domain={[0, 100]}
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  stroke="#1e293b"
                  tickCount={5}
                />
                <Legend
                  layout="horizontal"
                  align="center"
                  verticalAlign="bottom"
                  iconType="circle"
                  iconSize={8}
                  wrapperStyle={{ paddingTop: 10 }}
                />
                {filteredRows.map((row) => (
                  <Radar
                    key={row.model_id}
                    name={row.model_name}
                    dataKey={row.model_id}
                    stroke={getModelColor(row.model_id)}
                    fill={getModelColor(row.model_id)}
                    fillOpacity={0.15}
                    strokeWidth={2}
                    dot={false}
                  />
                ))}
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0c1322",
                    border: "1px solid #1e293b",
                    borderRadius: "8px",
                    boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                  }}
                  labelStyle={{ color: "#e2e8f0", fontWeight: 600 }}
                  itemStyle={{ fontSize: 12 }}
                  formatter={(value: number) => [`${value}/100`, "Score"]}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {viewMode === "bars" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Metric Bars */}
          <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6">
            <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-sky-400" />
              Key Metrics Comparison (0-100)
            </h3>
            <div className="h-[380px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barChartData.length > 0 ? barChartData : [{ name: "No Data", "Factual Consistency": 0, ROUGE: 0, Controllability: 0, Latency: 0, Cost: 0 }]} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis type="number" domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 11 }} stroke="#1e293b" />
                  <YAxis dataKey="name" type="category" width={120} tick={{ fill: "#e2e8f0", fontSize: 11 }} stroke="#1e293b" />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0c1322", border: "1px solid #1e293b", borderRadius: "8px" }}
                    labelStyle={{ color: "#e2e8f0", fontWeight: 600 }}
                    formatter={(value: number) => [`${value}/100`, "Score"]}
                  />
                  <Legend layout="horizontal" align="center" verticalAlign="bottom" wrapperStyle={{ paddingTop: 10 }} />
                  <Bar dataKey="Factual Consistency" name="Factual Consistency" fill="#10b981" radius={[0, 4, 4, 0]} />
                  <Bar dataKey="ROUGE-1" name="ROUGE-1" fill="#6366f1" radius={[0, 4, 4, 0]} />
                  <Bar dataKey="ROUGE-L" name="ROUGE-L" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                  <Bar dataKey="Controllability" name="Controllability" fill="#f59e0b" radius={[0, 4, 4, 0]} />
                  <Bar dataKey="Latency" name="Latency (Inverted)" fill="#ec4899" radius={[0, 4, 4, 0]} />
                  <Bar dataKey="Cost" name="Cost Efficiency" fill="#06b6d4" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Latency & Cost */}
          <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6">
            <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-amber-400" />
              Latency & Cost Analysis
            </h3>
            <div className="h-[380px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={latencyData.length > 0 ? latencyData : [{ name: "No Data", Latency: 0 }]} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis type="number" tick={{ fill: "#64748b", fontSize: 11 }} stroke="#1e293b" tickFormatter={(v) => `${v}ms`} />
                  <YAxis dataKey="name" type="category" width={120} tick={{ fill: "#e2e8f0", fontSize: 11 }} stroke="#1e293b" />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0c1322", border: "1px solid #1e293b", borderRadius: "8px" }}
                    labelStyle={{ color: "#e2e8f0", fontWeight: 600 }}
                    formatter={(value: number) => [`${value} ms`, "Latency"]}
                  />
                  <Bar dataKey="Latency" name="Latency (ms)" fill="#f59e0b" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {viewMode === "table" && (
        <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#090d16] border-b border-[#1e293b] text-[10px] uppercase text-slate-400">
                <tr>
                  <th className="py-3 px-4">Model</th>
                  <th className="py-3 px-4">Provider</th>
                  <th className="py-3 px-4">Format</th>
                  <th className="py-3 px-4">FCS</th>
                  <th className="py-3 px-4">ROUGE-1</th>
                  <th className="py-3 px-4">ROUGE-2</th>
                  <th className="py-3 px-4">ROUGE-L</th>
                  <th className="py-3 px-4">Controllability</th>
                  <th className="py-3 px-4">Latency (ms)</th>
                  <th className="py-3 px-4">Cost ($)</th>
                  <th className="py-3 px-4">Words</th>
                  <th className="py-3 px-4">Claims</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1e293b]">
                {filteredRows.length === 0 ? (
                  <tr>
                    <td colSpan={12} className="py-12 text-center text-slate-400">
                      No evaluation data available. Run transformations to generate comparisons.
                    </td>
                  </tr>
                ) : (
                  filteredRows.map((row) => (
                    <tr key={`${row.document_title}-${row.model_id}`} className="hover:bg-slate-800/50 transition-colors">
                      <td className="py-3 px-4 font-medium text-white truncate max-w-[150px]" title={row.model_name}>
                        {row.model_name.replace("Local Seq2Seq (", "").replace("Groq (", "").replace("Extractive Baseline (", "").replace(")", "")}
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={cn(
                            "text-[10px] font-semibold px-2 py-0.5 rounded uppercase",
                            row.provider === "LOCAL_EXTRACTIVE" && "bg-emerald-500/10 text-emerald-400",
                            row.provider === "LOCAL_SEQ2SEQ" && "bg-indigo-500/10 text-indigo-400",
                            row.provider === "GROQ" && "bg-amber-500/10 text-amber-400"
                          )}
                        >
                          {row.provider}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-300">{row.format_type.replace("_", " ")}</td>
                      <td className="py-3 px-4 font-mono font-semibold text-emerald-400">
                        {Math.round(row.factual_consistency_score * 100)}%
                      </td>
                      <td className="py-3 px-4 font-mono text-sky-400">{Math.round(row.rouge_1_f1 * 10000) / 100}</td>
                      <td className="py-3 px-4 font-mono text-slate-400">{Math.round(row.rouge_2_f1 * 10000) / 100}</td>
                      <td className="py-3 px-4 font-mono text-sky-400">{Math.round(row.rouge_l_f1 * 10000) / 100}</td>
                      <td className="py-3 px-4 font-mono font-semibold text-amber-400">
                        {Math.round(row.controllability_score * 100)}%
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-300">{row.latency_ms}</td>
                      <td className="py-3 px-4 font-mono text-slate-300">{row.estimated_cost_usd > 0 ? `$${row.estimated_cost_usd.toFixed(6)}` : "Free (Local)"}</td>
                      <td className="py-3 px-4 text-slate-300">{row.word_count}</td>
                      <td className="py-3 px-4 text-slate-300">{row.supported_claims}/{row.total_claims}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-[#0f172a] border border-[#1e293b]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Models Compared</span>
            <Sparkles className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-2xl font-bold text-white">{new Set(filteredRows.map((r) => r.model_id)).size}</div>
          <div className="text-[11px] text-slate-400 mt-1">Unique generation engines</div>
        </div>

        <div className="p-5 rounded-xl bg-[#0f172a] border border-[#1e293b]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Documents Evaluated</span>
            <BarChart3 className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white">{comparisons.length}</div>
          <div className="text-[11px] text-slate-400 mt-1">Benchmark documents tested</div>
        </div>

        <div className="p-5 rounded-xl bg-[#0f172a] border border-[#1e293b]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Avg Factual Consistency</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400">
            {filteredRows.length > 0
              ? Math.round(filteredRows.reduce((a, b) => a + b.factual_consistency_score, 0) / filteredRows.length * 100)
              : 0}%
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Mean FCS across all runs</div>
        </div>

        <div className="p-5 rounded-xl bg-[#0f172a] border border-[#1e293b]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Fastest Model</span>
            <TrendingUp className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {filteredRows.length > 0
              ? filteredRows.reduce((a, b) => (a.latency_ms < b.latency_ms ? a : b)).model_name.replace("Local Seq2Seq (", "").replace("Groq (", "").replace("Extractive Baseline (", "").replace(")", "")
              : "N/A"}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            {filteredRows.length > 0
              ? `${Math.min(...filteredRows.map((r) => r.latency_ms))} ms`
              : "N/A"}
          </div>
        </div>
      </div>
    </div>
  );
}
