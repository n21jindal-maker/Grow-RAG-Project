// ─── Query Types ──────────────────────────────────────────────────────────────
export type QueryType = "factual" | "advisory" | "pii" | "out_of_scope";

// ─── API Contract ──────────────────────────────────────────────────────────────
export interface ChatRequest {
  query: string;
}

export interface ChatResponse {
  answer: string;        // ≤ 3 sentences
  source_url: string;    // Citation URL
  last_updated: string;  // ISO date YYYY-MM-DD
  query_type: QueryType;
}

// ─── UI Message Model ─────────────────────────────────────────────────────────
export type MessageRole = "user" | "assistant";

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  source_url?: string;
  last_updated?: string;
  query_type?: QueryType;
  timestamp: Date;
  isLoading?: boolean;  // true while the bot is "thinking"
}

// ─── Chat Session ─────────────────────────────────────────────────────────────
export interface ChatSession {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}
