"use client";

import { motion } from "framer-motion";

interface SuggestionChipsProps {
  questions: string[];
  onChipClick: (text: string) => void;
}

export function SuggestionChips({ questions, onChipClick }: SuggestionChipsProps) {
  return (
    <div className="flex flex-wrap justify-center gap-3 w-full max-w-2xl">
      {questions.map((q, i) => (
        <motion.button
          key={q}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.28 + i * 0.08, duration: 0.28 }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.97 }}
          onClick={() => onChipClick(q)}
          className="bg-surface-container-lowest border border-outline-variant text-on-surface px-4 py-2.5 rounded-full text-body-md text-left hover:border-primary hover:text-primary transition-colors focus-visible:ring-2 focus-visible:ring-primary shadow-sm"
          aria-label={`Ask: ${q}`}
        >
          &ldquo;{q}&rdquo;
        </motion.button>
      ))}
    </div>
  );
}
