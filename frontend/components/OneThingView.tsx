"use client";

import { useState, useEffect } from "react";
import { getOneThing, markDone, skipCommitment } from "@/lib/api";
import type { Commitment } from "@/lib/api";

export function OneThingView() {
  const [thing, setThing] = useState<Commitment | null>(null);
  const [loading, setLoading] = useState(true);
  const [showWhy, setShowWhy] = useState(false);

  useEffect(() => {
    loadOneThing();
  }, []);

  async function loadOneThing() {
    setLoading(true);
    try {
      const data = await getOneThing();
      if ("extracted_task" in data) {
        setThing(data);
      } else {
        setThing(null);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }

  async function handleDone() {
    if (!thing) return;
    await markDone(thing.id);
    await loadOneThing();
  }

  async function handleSkip() {
    if (!thing) return;
    await skipCommitment(thing.id);
    await loadOneThing();
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[80vh]">
        <div className="text-zinc-500">Finding your one thing...</div>
      </div>
    );
  }

  if (!thing) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh]">
        <div className="text-2xl text-zinc-300 mb-2">All clear</div>
        <div className="text-zinc-500">No pending commitments</div>
        <button onClick={loadOneThing} className="btn btn-ghost mt-4">
          Refresh
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] px-4">
      <div className="text-2xl font-medium text-center mb-2 max-w-lg">
        {thing.extracted_task}
      </div>
      <div className="text-zinc-500 text-sm mb-8">
        from {thing.source}
        {thing.deadline && ` • due ${new Date(thing.deadline).toLocaleDateString()}`}
      </div>
      <div className="flex gap-4">
        <button onClick={handleDone} className="btn btn-primary">
          Done
        </button>
        <button onClick={handleSkip} className="btn btn-ghost">
          Skip
        </button>
        <button onClick={() => setShowWhy(!showWhy)} className="btn btn-ghost">
          Why this?
        </button>
      </div>
      {showWhy && (
        <div className="mt-4 text-zinc-500 text-sm">
          Priority: {thing.priority}/3 • Source: {thing.source}
        </div>
      )}
    </div>
  );
}
