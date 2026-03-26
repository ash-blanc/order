"use client";

import { useState } from "react";
import { chat } from "@/lib/api";

export function ConversationView() {
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSend() {
    if (!input.trim() || loading) return;
    
    const userMessage = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);
    
    try {
      const data = await chat(userMessage);
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
    } catch (e) {
      console.error(e);
    }
    
    setLoading(false);
  }

  return (
    <div className="flex flex-col h-[80vh] max-w-2xl mx-auto px-4">
      <div className="text-2xl font-medium text-center mb-8">Let's think through it</div>
      
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={msg.role === "user" ? "text-right" : "text-left"}>
            <div className={`inline-block max-w-[80%] p-3 rounded-lg ${
              msg.role === "user" ? "bg-zinc-800 text-white" : "bg-zinc-900 text-zinc-300"
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="text-left">
            <div className="inline-block p-3 rounded-lg bg-zinc-900 text-zinc-500">
              Thinking...
            </div>
          </div>
        )}
      </div>
      
      <div className="flex gap-2 pb-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="What's weighing on you?"
          className="flex-1 bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-2 text-white placeholder-zinc-600 focus:outline-none focus:border-zinc-700"
        />
        <button onClick={handleSend} className="btn btn-primary" disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}
