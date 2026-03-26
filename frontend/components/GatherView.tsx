"use client";

import { useState } from "react";
import { gatherAll, testConnections } from "@/lib/api";

export function GatherView() {
  const [loading, setLoading] = useState(false);
  const [connections, setConnections] = useState<Record<string, boolean> | null>(null);
  const [result, setResult] = useState<any>(null);

  async function handleTest() {
    const conns = await testConnections();
    setConnections(conns);
  }

  async function handleGather() {
    setLoading(true);
    try {
      const data = await gatherAll();
      setResult(data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] px-4">
      <div className="text-2xl font-medium mb-8">Gather from your scattered life</div>
      
      <div className="flex gap-4 mb-8">
        <button onClick={handleTest} className="btn btn-ghost">
          Test Connections
        </button>
        <button onClick={handleGather} className="btn btn-primary" disabled={loading}>
          {loading ? "Gathering..." : "Gather All"}
        </button>
      </div>

      {connections && (
        <div className="card w-full max-w-md mb-4">
          <div className="text-zinc-400 text-sm mb-2">Connections:</div>
          {Object.entries(connections).map(([source, connected]) => (
            <div key={source} className="flex justify-between py-1">
              <span className="text-zinc-300">{source}</span>
              <span className={connected ? "text-green-400" : "text-red-400"}>
                {connected ? "✓" : "✗"}
              </span>
            </div>
          ))}
        </div>
      )}

      {result && (
        <div className="card w-full max-w-md">
          <div className="text-zinc-400 text-sm mb-2">Results:</div>
          <div className="text-zinc-300">{result.status}</div>
          {result.results?.map((r: any, i: number) => (
            <div key={i} className="py-1 border-t border-zinc-800 mt-2">
              <div className="text-zinc-300">{r.source}: {r.total_found} found</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
