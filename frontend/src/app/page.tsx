"use client";

import Link from "next/link";
import {
  FileText,
  Sparkles,
  CheckCircle2,
  Cpu,
  BarChart3,
  ShieldCheck,
  ArrowRight,
  TrendingUp,
  Layers,
  Clock,
} from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Hero Banner */}
      <div className="relative rounded-2xl bg-gradient-to-r from-sky-950/40 via-indigo-950/30 to-slate-900 border border-sky-500/20 p-8 overflow-hidden shadow-2xl">
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Smart India Hackathon 2026 Core Platform</span>
          </div>
          <h2 className="text-3xl font-bold tracking-tight text-white">
            Automated Content Transformation with Verifiable Factual Grounding
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed">
            One source of truth. Transform government reports, policies, and white papers into
            calibrated <strong>Executive Summaries</strong>, <strong>Public Advisories</strong>,{" "}
            <strong>Social Media Posts</strong>, and <strong>FAQs</strong>. Cross-evaluated across
            Extractive, Local Seq2Seq (FLAN-T5/BART), and Groq LLM paradigms.
          </p>
          <div className="flex items-center gap-4 pt-2">
            <Link
              href="/transform"
              className="inline-flex items-center gap-2 bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold text-xs px-5 py-2.5 rounded-lg shadow-lg shadow-sky-500/25 transition-all"
            >
              <span>Launch Transformation Studio</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/documents"
              className="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-xs px-5 py-2.5 rounded-lg border border-slate-700 transition-all"
            >
              <FileText className="w-4 h-4 text-slate-400" />
              <span>Document Library</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-[#0f172a] border border-[#1e293b]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Generation Paradigms</span>
            <Cpu className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-2xl font-bold text-white">3 Engines</div>
          <div className="text-[11px] text-slate-400 mt-1">Extractive · Seq2Seq · Groq</div>
        </div>

        <div className="p-5 rounded-xl bg-[#0f172a] border border-[#1e293b]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Target Formats</span>
            <Layers className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white">4 Formats</div>
          <div className="text-[11px] text-slate-400 mt-1">Summary · Advisory · Social · FAQ</div>
        </div>

        <div className="p-5 rounded-xl bg-[#0f172a] border border-[#1e293b]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Fact Verification</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400">5 Statuses</div>
          <div className="text-[11px] text-slate-400 mt-1">Supported to Contradicted</div>
        </div>

        <div className="p-5 rounded-xl bg-[#0f172a] border border-[#1e293b]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Evaluation Rubrics</span>
            <BarChart3 className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-white">5 Dimensions</div>
          <div className="text-[11px] text-slate-400 mt-1">Coverage · ROUGE · Consistency · Speed</div>
        </div>
      </div>

      {/* Feature Deep Dive */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-xl bg-[#0f172a] border border-[#1e293b] space-y-3">
          <div className="w-10 h-10 rounded-lg bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
            <Layers className="w-5 h-5" />
          </div>
          <h3 className="text-base font-semibold text-white">Multi-Audience Controllability</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Calibrate readability, tone, length, required keywords, and prohibited claims to meet the
            communication standards of senior leaders, citizens, and social audiences.
          </p>
        </div>

        <div className="p-6 rounded-xl bg-[#0f172a] border border-[#1e293b] space-y-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <h3 className="text-base font-semibold text-white">Grounded Factual Verification</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Atomic claims (dates, numbers, entities, policies) are automatically extracted and verified
            against source chunks, with direct traceability highlighting.
          </p>
        </div>

        <div className="p-6 rounded-xl bg-[#0f172a] border border-[#1e293b] space-y-3">
          <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <BarChart3 className="w-5 h-5" />
          </div>
          <h3 className="text-base font-semibold text-white">3-Way Empirical Benchmark</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Measure and compare Extractive, FLAN-T5/BART, and Groq LLMs on the same input using
            ROUGE, BERTScore, Factual Consistency Score, and generation latency.
          </p>
        </div>
      </div>
    </div>
  );
}
