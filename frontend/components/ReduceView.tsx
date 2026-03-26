"use client";

import { useState } from "react";
import { reduceCommitments, getStats } from "@/lib/api";

export function ReduceView() {
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<{ pending: number; done: number; ignored: number; expired: number } | null>(null);
  const [result, setResult] = useState<any>(null);

  async function handleStats() {
    const data = await getStats();
    setStats(data);
  }

  async function handleReduce() {
    setLoading(true);
    try {
      const data = await reduceCommitments();
      setResult(data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] px-4">
      <div className="text-2xl font-medium mb-8">Filter noise, keep what matters</div>
      
      <div className="flex gap-4 mb-8">
        <button onClick={handleStats} className="btn btn-ghost">
          Get Stats
        </button>
        <button onClick={handleReduce} className="btn btn-primary" disabled={loading}>
          {loading ? "Reducing..." : "Reduce"}
        </button>
      </div>

      {stats && (
        <div className="card w-full max-w-md mb-4">
          <div className="text-zinc-400 text-sm mb-2">Current state:</div>
          <div className="grid grid-cols-2 gap-2">
            <div className="text-zinc-300">Pending: {stats.pending}</div>
            <div className="text-zinc-300">Done: {stats.done}</div>
            <div className="text-zinc-300">Ignored: {stats.ignored}</div>
            <div className="text-zinc-300">Expired: {stats.expired}</div>
          </div>
        </div>
      )}

      {result && (
        <div className="card w-full max-w-md">
          <div className="text-zinc-300">
            {result.total_before} → {result.total_after} commitments
          </div>
          <div className="text-zinc-500 text-sm mt-2">
            {result.ignored?.length || 0} marked as ignored
          </div>
        </div>
      )}
    </div>
  );
}
