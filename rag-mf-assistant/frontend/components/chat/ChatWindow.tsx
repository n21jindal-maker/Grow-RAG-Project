"use client";

import { useRef, useEffect } from "react";
import { AnimatePresence } from "framer-motion";
import type { Message } from "@/lib/types";
import { MessageBubble } from "./MessageBubble";
import { WelcomeScreen } from "./WelcomeScreen";

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  onChipClick: (text: string) => void;
}

export function ChatWindow({ messages, isLoading, onChipClick }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const isEmpty = messages.length === 0;

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <main
      role="log"
      aria-label="Chat conversation"
      aria-live="polite"
      className="flex-1 overflow-y-auto chat-scrollbar px-4 md:px-10 py-6"
    >
      {isEmpty ? (
        <WelcomeScreen onChipClick={onChipClick} />
      ) : (
        <div className="max-w-3xl mx-auto flex flex-col gap-4">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
          </AnimatePresence>
        </div>
      )}
      <div ref={bottomRef} className="h-1" />
    </main>
  );
}
