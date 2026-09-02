import type { ChatResponse } from "./types";

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "/api").replace(/\/$/, "");

/**
 * Send a user query to the FastAPI backend and return the typed response.
 * Throws on network errors or non-2xx HTTP status.
 */
export async function sendMessage(query: string): Promise<ChatResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30_000); // 30-second timeout

  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
      signal: controller.signal,
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => "Unknown error");
      throw new Error(
        `API error ${response.status}: ${errorText}`
      );
    }

    const data: ChatResponse = await response.json();
    return data;
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      throw new Error("Request timed out. Please try again.");
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Send a user query to the FastAPI backend and stream the response back.
 */
export async function sendMessageStream(
  query: string,
  onEvent: (event: any) => void
): Promise<void> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 60_000); // 60-second timeout for streaming

  try {
    const response = await fetch(`${API_BASE}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
      signal: controller.signal,
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => "Unknown error");
      throw new Error(`API error ${response.status}: ${errorText}`);
    }

    if (!response.body) {
      throw new Error("Response body is null");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      
      // Keep the last incomplete line in the buffer
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const dataStr = line.slice(6);
          try {
            const data = JSON.parse(dataStr);
            onEvent(data);
          } catch (e) {
            console.error("Error parsing SSE JSON:", e, dataStr);
          }
        }
      }
    }
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      throw new Error("Request timed out. Please try again.");
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}
