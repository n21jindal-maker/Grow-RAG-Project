"use client";

import { motion } from "framer-motion";
import { XCircle } from "lucide-react";

interface ToastProps {
  message: string;
}

export function Toast({ message }: ToastProps) {
  return (
    <motion.div
      initial={{ x: 120, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 120, opacity: 0 }}
      transition={{ type: "spring", damping: 22, stiffness: 260 }}
      role="alert"
      className="fixed bottom-6 right-6 z-50 flex items-center gap-3 bg-on-surface text-inverse-on-surface text-body-md font-medium px-4 py-3 rounded-xl shadow-toast max-w-xs"
    >
      <XCircle size={18} className="text-error-container shrink-0" aria-hidden />
      <span>{message}</span>
    </motion.div>
  );
}
