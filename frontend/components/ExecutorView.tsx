"use client";

import { useState, useEffect } from "react";
import { listCommitments } from "@/lib/api";
import type { Commitment } from "@/lib/api";

export function ExecutorView() {
  const [commitments, setCommitments] = useState<Commitment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCommitments();
  }, []);

  async function loadCommitments() {
    try {
      const data = await listCommitments();
      setCommitments(data.commitments);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] px-4">
      <div className="text-2xl font-medium mb-8">Ready to act</div>
      
      {loading ? (
        <div className="text-zinc-500">Loading commitments...</div>
      ) : commitments.length === 0 ? (
        <div className="text-zinc-500">No commitments found</div>
      ) : (
        <div className="w-full max-w-md space-y-2">
          {commitments.map((c) => (
            <div key={c.id} className="card flex justify-between items-center">
              <div>
                <div className="text-zinc-200">{c.extracted_task}</div>
                <div className="text-zinc-500 text-sm">{c.source}</div>
              </div>
              <button className="btn btn-ghost text-sm">Handle</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
