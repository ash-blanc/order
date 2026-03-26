const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  
  if (!res.ok) {
    throw new Error(`API Error: ${res.status}`);
  }
  
  return res.json();
}

// Types
export interface Commitment {
  id: string;
  source: string;
  text: string;
  extracted_task: string;
  platform_url: string;
  deadline: string | null;
  priority: number;
  status: string;
  created_at: string;
}

// One-Thing
export async function getOneThing() {
  return fetchApi<Commitment | { status: string; message: string }>("/api/one-thing");
}

export async function markDone(id: string) {
  return fetchApi("/api/one-thing/done", {
    method: "POST",
    body: JSON.stringify({ commitment_id: id }),
  });
}

export async function skipCommitment(id: string) {
  return fetchApi("/api/one-thing/skip", {
    method: "POST",
    body: JSON.stringify({ commitment_id: id }),
  });
}

// Gather
export async function gatherAll() {
  return fetchApi<{ status: string; results: any[] }>("/api/gather");
}

export async function testConnections() {
  return fetchApi<Record<string, boolean>>("/api/gather/test");
}

// Reduce
export async function reduceCommitments() {
  return fetchApi<any>("/api/reduce");
}

export async function getStats() {
  return fetchApi<{ pending: number; done: number; ignored: number; expired: number }>("/api/stats");
}

// Conversation
export async function chat(message: string) {
  return fetchApi<{ response: string }>("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}

// Just-in-Time
export async function searchCommitments(query: string) {
  return fetchApi<{ results: Commitment[] }>("/api/search", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}

export async function getPromises(timeframe = "this week") {
  return fetchApi<{ results: Commitment[] }>(`/api/promises?timeframe=${timeframe}`);
}

// Commitments
export async function listCommitments() {
  return fetchApi<{ commitments: Commitment[] }>("/api/commitments");
}
