"use client";

import { useState } from "react";
import { searchCommitments, getPromises } from "@/lib/api";
import type { Commitment } from "@/lib/api";

export function JustInTimeView() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Commitment[]>([]);
  const [loading, setLoading] = useState(false);

  async function handleSearch() {
    if (!query.trim() || loading) return;
    setLoading(true);
    try {
      const data = await searchCommitments(query);
      setResults(data.results);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }

  async function handlePromises() {
    setLoading(true);
    try {
      const data = await getPromises();
      setResults(data.results);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] px-4">
      <div className="text-2xl font-medium mb-8">Ask and receive</div>
      
      <div className="flex gap-2 w-full max-w-md mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          placeholder="What did I promise about X?"
          className="flex-1 bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-2 text-white placeholder-zinc-600 focus:outline-none focus:border-zinc-700"
        />
        <button onClick={handleSearch} className="btn btn-primary" disabled={loading}>
          Search
        </button>
      </div>
      
      <button onClick={handlePromises} className="btn btn-ghost mb-8">
        What did I promise?
      </button>

      {results.length > 0 && (
        <div className="w-full max-w-md space-y-2">
          {results.map((c) => (
            <div key={c.id} className="card">
              <div className="text-zinc-200">{c.extracted_task}</div>
              <div className="text-zinc-500 text-sm mt-1">
                {c.source} • {c.status}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
