"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FileText,
  Sparkles,
  CheckCircle2,
  Cpu,
  BarChart3,
  Database,
  ShieldCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigationItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Document Library", href: "/documents", icon: FileText },
  { name: "Transformation Studio", href: "/transform", icon: Sparkles },
  { name: "Review & Traceability", href: "/review", icon: CheckCircle2 },
  { name: "Model Laboratory", href: "/models", icon: Cpu },
  { name: "Evaluation Dashboard", href: "/evaluation", icon: BarChart3 },
  { name: "Dataset Management", href: "/datasets", icon: Database },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-[#1e293b] bg-[#0c1322] flex flex-col h-screen sticky top-0">
      {/* Brand Header */}
      <div className="h-16 border-b border-[#1e293b] flex items-center px-6 gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/20 font-bold text-lg">
          A
        </div>
        <div>
          <span className="font-semibold text-sm tracking-tight text-white block">
            ACTP Engine
          </span>
          <span className="text-[11px] text-sky-400 font-medium block">
            SIH 2026 Edition
          </span>
        </div>
      </div>

      {/* Nav List */}
      <div className="flex-1 py-6 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 mb-2 text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
          Workspaces
        </div>
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all",
                isActive
                  ? "bg-sky-500/10 text-sky-400 border border-sky-500/30 font-semibold"
                  : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/40"
              )}
            >
              <Icon className={cn("w-4 h-4", isActive ? "text-sky-400" : "text-slate-400")} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-[#1e293b] bg-[#090e1a]">
        <div className="flex items-center gap-2 text-xs text-emerald-400 font-medium mb-1">
          <ShieldCheck className="w-4 h-4" />
          <span>Factual Grounding Engine</span>
        </div>
        <p className="text-[11px] text-slate-400">
          Extractive · Seq2Seq · Groq
        </p>
      </div>
    </aside>
  );
}
