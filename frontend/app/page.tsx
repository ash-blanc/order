"use client";

import { useState } from "react";
import { ModeSelector, type Mode } from "@/components/ModeSelector";
import { OneThingView } from "@/components/OneThingView";
import { GatherView } from "@/components/GatherView";
import { ReduceView } from "@/components/ReduceView";
import { ConversationView } from "@/components/ConversationView";
import { JustInTimeView } from "@/components/JustInTimeView";
import { ExecutorView } from "@/components/ExecutorView";

export default function Home() {
  const [mode, setMode] = useState<Mode>("drowning");

  const renderView = () => {
    switch (mode) {
      case "drowning":
        return <OneThingView />;
      case "scattered":
        return <GatherView />;
      case "stuck":
        return <ConversationView />;
      case "accumulated":
        return <ReduceView />;
      case "specific":
        return <JustInTimeView />;
      case "ready":
        return <ExecutorView />;
    }
  };

  return (
    <main className="min-h-screen bg-zinc-950">
      {/* Header */}
      <header className="border-b border-zinc-800">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="text-xl font-medium">Order</div>
          <div className="text-zinc-500 text-sm">Bring order to chaos</div>
        </div>
      </header>

      {/* Mode Selector */}
      <ModeSelector mode={mode} onChange={setMode} />

      {/* Thin bar */}
      <div className="thin-bar" />

      {/* Main View */}
      {renderView()}
    </main>
  );
}
