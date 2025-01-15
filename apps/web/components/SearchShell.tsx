"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { ResultCard } from "./ResultCard";
import { SearchResponse, SearchResult } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";
const PLATFORMS = ["all", "reddit", "telegram", "x", "devpost", "linkedin"] as const;

function useDebounced<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState<T>(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timer);
  }, [value, delayMs]);
  return debounced;
}

export function SearchShell() {
  const [query, setQuery] = useState("AI engineer Ethiopia");
  const [platform, setPlatform] = useState<(typeof PLATFORMS)[number]>("all");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [sortBy, setSortBy] = useState<"relevance" | "latest">("relevance");
  const [page, setPage] = useState(1);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const debouncedQuery = useDebounced(query, 250);

  const effectiveQuery = useMemo(() => {
    if (platform === "all") {
      return debouncedQuery;
    }
    return `platform:${platform} ${debouncedQuery}`.trim();
  }, [debouncedQuery, platform]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "/") {
        event.preventDefault();
        inputRef.current?.focus();
      }
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        inputRef.current?.focus();
        inputRef.current?.select();
      }
      if (event.key === "ArrowDown") {
        event.preventDefault();
        setSelectedIndex((prev) => Math.min(prev + 1, Math.max(0, pagedResults.length - 1)));
      }
      if (event.key === "ArrowUp") {
        event.preventDefault();
        setSelectedIndex((prev) => Math.max(prev - 1, 0));
      }
      if (event.key === "Enter") {
        const selected = pagedResults[selectedIndex];
        if (selected) {
          window.open(selected.url, "_blank", "noopener,noreferrer");
        }
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  });

  useEffect(() => {
    if (!effectiveQuery.trim()) {
      setResults([]);
      setTotal(0);
      return;
    }

    const controller = new AbortController();

    async function runSearch() {
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(effectiveQuery)}`, {
          signal: controller.signal
        });
        if (!response.ok) {
          throw new Error(`Search failed: ${response.status}`);
        }
        const payload = (await response.json()) as SearchResponse;
        setResults(payload.results);
        setTotal(payload.total);
        setSelectedIndex(0);
      } catch {
        setResults([]);
        setTotal(0);
      } finally {
        setLoading(false);
      }
    }

    runSearch();
    return () => controller.abort();
  }, [effectiveQuery]);

  const sortedResults = useMemo(() => {
    if (sortBy === "latest") {
      return [...results].sort((a, b) => {
        const aTime = a.created_at ? new Date(a.created_at).getTime() : 0;
        const bTime = b.created_at ? new Date(b.created_at).getTime() : 0;
        return bTime - aTime;
      });
    }
    return results;
  }, [results, sortBy]);

  const pageSize = 10;
  const pagedResults = sortedResults.slice((page - 1) * pageSize, page * pageSize);
  const maxPage = Math.max(1, Math.ceil(sortedResults.length / pageSize));

  useEffect(() => {
    setPage(1);
  }, [effectiveQuery, sortBy]);

  return (
    <main className="mx-auto min-h-screen w-full max-w-5xl px-4 py-10 sm:px-8">
      <section className="mb-8 rounded-2xl border border-white/10 bg-panel/70 p-5 backdrop-blur">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">Surf</h1>
            <p className="text-sm text-muted">Hybrid local search for the developer internet</p>
          </div>
          <div className="rounded-lg border border-accent/30 bg-accent/10 px-2 py-1 text-xs text-accent">
            local-first
          </div>
        </div>

        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search people, jobs, hackathons, discussions..."
          className="w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-text outline-none ring-accent transition focus:border-accent focus:ring-1"
        />

        <div className="mt-4 flex flex-wrap items-center gap-2">
          {PLATFORMS.map((option) => (
            <button
              key={option}
              onClick={() => setPlatform(option)}
              className={`rounded-full border px-3 py-1 text-xs uppercase tracking-wide ${
                option === platform
                  ? "border-accent bg-accent/15 text-accent"
                  : "border-white/15 bg-white/5 text-muted hover:text-text"
              }`}
            >
              {option}
            </button>
          ))}

          <select
            value={sortBy}
            onChange={(event) => setSortBy(event.target.value as "relevance" | "latest")}
            className="ml-auto rounded-lg border border-white/10 bg-black/20 px-2 py-1 text-xs text-text"
          >
            <option value="relevance">Relevance</option>
            <option value="latest">Latest</option>
          </select>
        </div>

        <div className="mt-3 flex items-center justify-between text-xs text-muted">
          <span>{loading ? "Searching..." : `${total} results`}</span>
          <span>/ focus, arrows navigate, Enter open, Ctrl/Cmd+K</span>
        </div>
      </section>

      <section className="space-y-3">
        {pagedResults.map((result, idx) => (
          <ResultCard key={result.id} result={result} selected={selectedIndex === idx} />
        ))}

        {!loading && pagedResults.length === 0 ? (
          <div className="rounded-xl border border-dashed border-white/20 bg-panel/40 p-8 text-center text-sm text-muted">
            No results yet. Run indexing from the API or CLI and try again.
          </div>
        ) : null}
      </section>

      <section className="mt-6 flex items-center justify-between text-xs text-muted">
        <button
          onClick={() => setPage((prev) => Math.max(1, prev - 1))}
          disabled={page <= 1}
          className="rounded-lg border border-white/10 px-3 py-1 disabled:opacity-40"
        >
          Prev
        </button>
        <span>
          Page {page} / {maxPage}
        </span>
        <button
          onClick={() => setPage((prev) => Math.min(maxPage, prev + 1))}
          disabled={page >= maxPage}
          className="rounded-lg border border-white/10 px-3 py-1 disabled:opacity-40"
        >
          Next
        </button>
      </section>
    </main>
  );
}
