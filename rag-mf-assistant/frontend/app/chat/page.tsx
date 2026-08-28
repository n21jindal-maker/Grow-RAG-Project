"use client";

import { useReducer, useCallback, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { InputBar } from "@/components/chat/InputBar";
import { Toast } from "@/components/ui/Toast";
import { sendMessage } from "@/lib/api";
import type { ChatSession, Message } from "@/lib/types";

// ─── State & Reducer ──────────────────────────────────────────────────────────

type Action =
  | { type: "ADD_USER_MSG"; payload: Message }
  | { type: "ADD_BOT_MSG"; payload: Message }
  | { type: "REPLACE_LOADING_MSG"; payload: Message }
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "SET_ERROR"; payload: string | null }
  | { type: "CLEAR_CHAT" };

function chatReducer(state: ChatSession, action: Action): ChatSession {
  switch (action.type) {
    case "ADD_USER_MSG":
      return { ...state, messages: [...state.messages, action.payload] };
    case "ADD_BOT_MSG":
      return { ...state, messages: [...state.messages, action.payload] };
    case "REPLACE_LOADING_MSG":
      return {
        ...state,
        messages: state.messages.map((m) =>
          m.isLoading ? action.payload : m
        ),
      };
    case "SET_LOADING":
      return { ...state, isLoading: action.payload };
    case "SET_ERROR":
      return { ...state, error: action.payload };
    case "CLEAR_CHAT":
      return { messages: [], isLoading: false, error: null };
    default:
      return state;
  }
}

const initialState: ChatSession = {
  messages: [],
  isLoading: false,
  error: null,
};

// ─── Page Component ───────────────────────────────────────────────────────────

export default function ChatPage() {
  const [state, dispatch] = useReducer(chatReducer, initialState);
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3500);
  };

  const handleNewAnalysis = useCallback(() => {
    dispatch({ type: "CLEAR_CHAT" });
  }, []);

  const handleSend = useCallback(
    async (query: string) => {
      if (!query.trim() || state.isLoading) return;

      // 1. Add user message immediately
      const userMsg: Message = {
        id: `user-${Date.now()}`,
        role: "user",
        content: query,
        timestamp: new Date(),
      };
      dispatch({ type: "ADD_USER_MSG", payload: userMsg });

      // 2. Add loading placeholder bubble
      const loadingMsg: Message = {
        id: `loading-${Date.now()}`,
        role: "assistant",
        content: "",
        timestamp: new Date(),
        isLoading: true,
      };
      dispatch({ type: "ADD_BOT_MSG", payload: loadingMsg });
      dispatch({ type: "SET_LOADING", payload: true });

      // 3. Call API
      try {
        const response = await sendMessage(query);

        const botMsg: Message = {
          id: `bot-${Date.now()}`,
          role: "assistant",
          content: response.answer,
          source_url: response.source_url,
          last_updated: response.last_updated,
          query_type: response.query_type,
          timestamp: new Date(),
          isLoading: false,
        };
        dispatch({ type: "REPLACE_LOADING_MSG", payload: botMsg });
      } catch (err) {
        const errMsg: Message = {
          id: `err-${Date.now()}`,
          role: "assistant",
          content:
            "I encountered an error fetching your answer. Please try again.",
          query_type: "out_of_scope",
          timestamp: new Date(),
          isLoading: false,
        };
        dispatch({ type: "REPLACE_LOADING_MSG", payload: errMsg });
        showToast(err instanceof Error ? err.message : "Unexpected error");
      } finally {
        dispatch({ type: "SET_LOADING", payload: false });
      }
    },
    [state.isLoading]
  );

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <Sidebar onNewAnalysis={handleNewAnalysis} />

      {/* Main area */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <TopBar />

        {/* Chat + Input */}
        <div className="flex flex-col flex-1 overflow-hidden relative">
          <ChatWindow
            messages={state.messages}
            isLoading={state.isLoading}
            onChipClick={handleSend}
          />

          <InputBar
            onSend={handleSend}
            isLoading={state.isLoading}
          />
        </div>
      </div>

      {/* Error Toast */}
      {toastMsg && <Toast message={toastMsg} />}
    </div>
  );
}
