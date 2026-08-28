"use client";

import { useRef, useState, useCallback, useEffect } from "react";
import { motion } from "framer-motion";
import { ArrowUp, Loader2 } from "lucide-react";

interface InputBarProps {
  onSend: (text: string) => void;
  isLoading: boolean;
}

const MAX_CHARS = 500;

export function InputBar({ onSend, isLoading }: InputBarProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 160)}px`;
  }, [value]);

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [value, isLoading, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const canSend = value.trim().length > 0 && !isLoading;
  const charCount = value.length;
  const nearLimit = charCount > 400;

  return (
    /* Gradient fade from background at the bottom */
    <div className="shrink-0 px-4 md:px-10 pb-6 pt-4 bg-gradient-to-t from-background via-background to-transparent">
      <div className="max-w-3xl mx-auto">
        {/* Character count warning */}
        {nearLimit && (
          <p className="text-label-md text-right mb-1 text-on-surface-variant">
            <span className={charCount >= MAX_CHARS ? "text-error font-semibold" : ""}>
              {charCount}
            </span>
            /{MAX_CHARS}
          </p>
        )}

        {/* Input container */}
        <div
          className={`flex items-end gap-2 bg-surface-container-lowest border rounded-xl p-2 shadow-card transition-all duration-200 ${
            value.length > 0
              ? "border-primary/50 shadow-input-focus"
              : "border-outline-variant"
          }`}
        >
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => {
              if (e.target.value.length <= MAX_CHARS) setValue(e.target.value);
            }}
            onKeyDown={handleKeyDown}
            placeholder="Type your question..."
            rows={1}
            maxLength={MAX_CHARS}
            disabled={isLoading}
            aria-label="Chat input"
            className="flex-1 bg-transparent border-0 resize-none outline-none py-2 px-2 text-body-md text-on-surface placeholder:text-on-surface-variant/60 disabled:opacity-60 max-h-40"
          />

          {/* Send button */}
          <motion.button
            whileTap={{ scale: 0.88 }}
            onClick={handleSend}
            disabled={!canSend}
            aria-label="Send message"
            className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 mb-0.5 mr-0.5 transition-colors focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 ${
              canSend
                ? "bg-primary text-white hover:opacity-90 cursor-pointer"
                : "bg-surface-container-high text-on-surface-variant cursor-not-allowed opacity-60"
            }`}
          >
            {isLoading ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <ArrowUp size={18} strokeWidth={2.5} />
            )}
          </motion.button>
        </div>

        <p className="text-label-md text-on-surface-variant/60 text-center mt-2">
          Press Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
