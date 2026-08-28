"use client";

import { motion } from "framer-motion";
import { TrendingUp, Lock, Info, CheckCircle2 } from "lucide-react";
import type { Message } from "@/lib/types";
import { CitationLink } from "../ui/CitationLink";
import { DisclaimerBanner } from "../ui/DisclaimerBanner";
import { LoadingDots } from "../ui/LoadingDots";

interface MessageBubbleProps {
  message: Message;
}

// Icon per query_type for bot messages
const queryTypeIcon = {
  factual: <CheckCircle2 size={14} className="text-primary shrink-0" />,
  advisory: <Info size={14} className="text-amber-500 shrink-0" />,
  pii: <Lock size={14} className="text-error shrink-0" />,
  out_of_scope: <Info size={14} className="text-secondary shrink-0" />,
};

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}
    >
      {isUser ? (
        /* ── User Bubble ─────────────────────────────────────────── */
        <div className="max-w-[80%] md:max-w-[72%] bg-primary text-white rounded-lg rounded-br-sm px-4 py-3 shadow-sm">
          <p className="text-body-md leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>
      ) : (
        /* ── Assistant Bubble ────────────────────────────────────── */
        <div
          className={`max-w-[80%] md:max-w-[72%] bg-surface-container-lowest border rounded-lg rounded-bl-sm px-4 py-3 shadow-card flex flex-col gap-2 ${
            message.query_type === "pii"
              ? "border-error-container bg-error-container/20"
              : "border-surface-variant"
          }`}
        >
          {message.isLoading ? (
            <LoadingDots />
          ) : (
            <>
              {/* Answer text */}
              <p className="text-body-md text-on-surface leading-relaxed whitespace-pre-wrap">
                {message.content}
              </p>

              {/* Advisory disclaimer inline */}
              {message.query_type === "advisory" && <DisclaimerBanner />}

              {/* Citation + date footer */}
              {message.source_url && (
                <div className="flex flex-wrap items-center gap-2 pt-2 mt-1 border-t border-surface-variant/60">
                  {message.query_type && queryTypeIcon[message.query_type]}
                  <CitationLink url={message.source_url} />
                  {message.last_updated && (
                    <span className="text-label-md text-on-surface-variant/70 ml-auto">
                      Last updated: {message.last_updated}
                    </span>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </motion.div>
  );
}
