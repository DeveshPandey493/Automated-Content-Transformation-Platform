"use client";

import { useEffect, useState } from "react";
import { Activity, Cpu, Database, CheckCircle, AlertCircle } from "lucide-react";

interface HealthData {
  status: string;
  database: string;
  database_engine: string;
  gpu?: {
    available: boolean;
    device_name?: string;
    total_vram_gb?: number;
  };
  groq_configured: boolean;
}

export function Header() {
  const [health, setHealth] = useState<HealthData | null>(null);

  useEffect(() => {
    fetch("/api/health")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setHealth(data))
      .catch(() => setHealth(null));
  }, []);

  return (
    <header className="h-16 border-b border-[#1e293b] bg-[#0c1322]/80 backdrop-blur px-8 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h1 className="text-sm font-semibold text-white tracking-tight">
          Gen AI Automated Content Transformation
        </h1>
        <p className="text-xs text-slate-400">
          Single Source of Truth · Multi-Audience · Grounded Fact Verification
        </p>
      </div>

      <div className="flex items-center gap-3">
        {/* System Status Pill */}
        <div className="flex items-center gap-2 bg-[#090e1a] border border-[#1e293b] px-3 py-1.5 rounded-full text-xs">
          <Activity className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-slate-300">Backend:</span>
          <span className="text-emerald-400 font-medium">
            {health?.status === "ok" ? "Online" : "Connecting..."}
          </span>
        </div>

        {/* Database Engine Pill */}
        <div className="flex items-center gap-2 bg-[#090e1a] border border-[#1e293b] px-3 py-1.5 rounded-full text-xs">
          <Database className="w-3.5 h-3.5 text-sky-400" />
          <span className="text-slate-300">DB:</span>
          <span className="text-sky-400 font-medium capitalize">
            {health?.database_engine || "SQLite"}
          </span>
        </div>

        {/* GPU Engine Pill */}
        <div className="flex items-center gap-2 bg-[#090e1a] border border-[#1e293b] px-3 py-1.5 rounded-full text-xs">
          <Cpu className="w-3.5 h-3.5 text-indigo-400" />
          <span className="text-slate-300">GPU:</span>
          <span className="text-indigo-400 font-medium">
            {health?.gpu?.available ? `${health.gpu.total_vram_gb} GB VRAM` : "CPU Mode"}
          </span>
        </div>
      </div>
    </header>
  );
}
