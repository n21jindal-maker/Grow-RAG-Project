"use client";

import { motion } from "framer-motion";
import { TrendingUp } from "lucide-react";
import { SuggestionChips } from "./SuggestionChips";

interface WelcomeScreenProps {
  onChipClick: (text: string) => void;
}

const EXAMPLE_QUESTIONS = [
  "What is the expense ratio of HDFC Mid-Cap Fund?",
  "What is the exit load for HDFC Gold ETF Fund?",
  "How do I download my account statement?",
];

export function WelcomeScreen({ onChipClick }: WelcomeScreenProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="flex flex-col items-center justify-center h-full min-h-[60vh] px-4 text-center"
    >
      {/* Animated icon */}
      <motion.div
        initial={{ scale: 0.85, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.1, duration: 0.35, ease: "easeOut" }}
        className="w-16 h-16 bg-surface-container-high rounded-full flex items-center justify-center mb-6 shadow-card"
      >
        <TrendingUp size={32} className="text-primary" strokeWidth={1.75} />
      </motion.div>

      {/* Heading */}
      <motion.h2
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15, duration: 0.3 }}
        className="text-headline-md font-semibold text-on-surface mb-2"
      >
        How can I assist you today?
      </motion.h2>

      {/* Subtitle */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.22, duration: 0.3 }}
        className="text-body-md text-on-surface-variant max-w-sm mb-8"
      >
        Ask me about fund facts, performance metrics, expense ratios, or account
        procedures.
      </motion.p>

      {/* Suggestion chips */}
      <SuggestionChips
        questions={EXAMPLE_QUESTIONS}
        onChipClick={onChipClick}
      />
    </motion.div>
  );
}
