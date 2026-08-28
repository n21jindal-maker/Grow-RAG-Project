"use client";

import { motion } from "framer-motion";

const dot = {
  animate: {
    scale: [0, 1, 0],
    opacity: [0.3, 1, 0.3],
  },
};

export function LoadingDots() {
  return (
    <div className="flex items-center gap-1.5 py-1" aria-label="Loading response">
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          variants={dot}
          animate="animate"
          transition={{
            duration: 1.2,
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 0.15,
          }}
          className="w-2 h-2 rounded-full bg-primary/70 block"
        />
      ))}
    </div>
  );
}
