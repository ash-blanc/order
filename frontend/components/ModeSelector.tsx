"use client";

export type Mode = "drowning" | "scattered" | "stuck" | "accumulated" | "specific" | "ready";

interface ModeSelectorProps {
  mode: Mode;
  onChange: (mode: Mode) => void;
}

const modes: { key: Mode; label: string; desc: string }[] = [
  { key: "drowning", label: "Drowning", desc: "I can't think" },
  { key: "scattered", label: "Scattered", desc: "I don't know..." },
  { key: "stuck", label: "Stuck", desc: "I know but..." },
  { key: "accumulated", label: "Accumulated", desc: "Too much on plate" },
  { key: "specific", label: "Specific", desc: "What about X?" },
  { key: "ready", label: "Ready", desc: "Just do it" },
];

export function ModeSelector({ mode, onChange }: ModeSelectorProps) {
  return (
    <div className="flex flex-wrap justify-center gap-2 p-4">
      {modes.map((m) => (
        <button
          key={m.key}
          onClick={() => onChange(m.key)}
          className={`mode-chip ${mode === m.key ? "active" : ""}`}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}
