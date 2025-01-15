"use client";

import { SearchResult } from "./types";

const PLATFORM_COLORS: Record<string, string> = {
  reddit: "bg-orange-500/20 text-orange-300 border-orange-300/30",
  telegram: "bg-sky-500/20 text-sky-300 border-sky-300/30",
  devpost: "bg-emerald-500/20 text-emerald-300 border-emerald-300/30",
  x: "bg-zinc-500/20 text-zinc-200 border-zinc-300/30",
  linkedin: "bg-blue-500/20 text-blue-300 border-blue-300/30"
};

type ResultCardProps = {
  result: SearchResult;
  selected: boolean;
};

export function ResultCard({ result, selected }: ResultCardProps) {
  const badgeClass = PLATFORM_COLORS[result.platform] ?? "bg-white/10 text-white border-white/20";
  return (
    <a
      href={result.url}
      target="_blank"
      rel="noreferrer"
      className={`fade-in block rounded-xl border p-4 transition-all ${
        selected
          ? "border-accent shadow-neon bg-panelAlt/80"
          : "border-white/10 bg-panel/60 hover:border-white/25 hover:bg-panelAlt/60"
      }`}
    >
      <div className="mb-3 flex items-center justify-between">
        <span className={`rounded-full border px-2 py-1 text-xs uppercase tracking-wide ${badgeClass}`}>
          {result.platform}
        </span>
        <span className="text-xs text-muted">score {result.score.toFixed(4)}</span>
      </div>
      <h3 className="mb-2 text-base font-semibold text-text">{result.title ?? "(no title)"}</h3>
      <p className="mb-3 text-sm leading-6 text-muted">{result.snippet}</p>
      <div className="flex items-center justify-between text-xs text-muted">
        <span>{result.author ?? "unknown"}</span>
        <span>{result.created_at ? new Date(result.created_at).toLocaleString() : "no date"}</span>
      </div>
    </a>
  );
}
