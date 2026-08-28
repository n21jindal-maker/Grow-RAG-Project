"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  TrendingUp,
  History,
  BarChart2,
  HelpCircle,
  Settings,
  LogOut,
  Plus,
  Menu,
  X,
} from "lucide-react";

interface SidebarProps {
  onNewAnalysis: () => void;
}

const navItems = [
  { icon: History, label: "Chat History", active: true },
  { icon: TrendingUp, label: "Market Insights", active: false },
  { icon: BarChart2, label: "Portfolio Analysis", active: false },
  { icon: HelpCircle, label: "Help & Support", active: false },
];

const bottomItems = [
  { icon: Settings, label: "Settings" },
  { icon: LogOut, label: "Log Out" },
];

export function Sidebar({ onNewAnalysis }: SidebarProps) {
  const [mobileOpen, setMobileOpen] = useState(false);

  const sidebarContent = (
    <div className="flex flex-col h-full p-4 gap-2">
      {/* Brand Header */}
      <div className="mb-4">
        <h1 className="text-title-lg font-bold text-primary leading-tight">
          Mutual Fund Assistant
        </h1>
        <p className="text-body-md text-secondary mt-0.5">Expert Assistant</p>
      </div>

      {/* New Analysis CTA */}
      <motion.button
        whileTap={{ scale: 0.96 }}
        onClick={() => {
          onNewAnalysis();
          setMobileOpen(false);
        }}
        className="flex items-center justify-center gap-2 w-full bg-primary text-white font-semibold rounded-full py-2.5 px-4 mb-2 hover:opacity-90 transition-opacity focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
        aria-label="Start new analysis"
      >
        <Plus size={18} strokeWidth={2.5} />
        New Analysis
      </motion.button>

      {/* Main Nav */}
      <nav className="flex-1 flex flex-col gap-1" aria-label="Main navigation">
        {navItems.map(({ icon: Icon, label, active }) => (
          <button
            key={label}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-body-md font-medium transition-colors text-left w-full ${
              active
                ? "bg-secondary-container text-on-secondary-container font-semibold"
                : "text-secondary hover:bg-surface-container-high"
            }`}
            aria-current={active ? "page" : undefined}
          >
            <Icon size={20} strokeWidth={1.75} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      {/* Bottom Nav */}
      <div className="mt-auto pt-3 border-t border-surface-variant flex flex-col gap-1">
        {bottomItems.map(({ icon: Icon, label }) => (
          <button
            key={label}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-body-md text-secondary hover:bg-surface-container-high transition-colors text-left w-full"
            aria-label={label}
          >
            <Icon size={20} strokeWidth={1.75} />
            <span>{label}</span>
          </button>
        ))}
      </div>
    </div>
  );

  return (
    <>
      {/* ── Desktop Sidebar ───────────────────────────────────────────── */}
      <aside className="hidden md:flex flex-col w-60 shrink-0 bg-surface-container-low border-r border-surface-variant h-screen overflow-y-auto no-scrollbar">
        {sidebarContent}
      </aside>

      {/* ── Mobile Hamburger ──────────────────────────────────────────── */}
      <div className="md:hidden fixed top-0 left-0 z-50 p-3">
        <button
          onClick={() => setMobileOpen(true)}
          aria-label="Open navigation menu"
          className="p-2 rounded-lg text-on-surface hover:bg-surface-container transition-colors"
        >
          <Menu size={22} />
        </button>
      </div>

      {/* ── Mobile Drawer ─────────────────────────────────────────────── */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 bg-black/30 z-40 md:hidden"
              onClick={() => setMobileOpen(false)}
            />
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: "spring", damping: 28, stiffness: 260 }}
              className="fixed left-0 top-0 bottom-0 w-72 bg-surface-container-low border-r border-surface-variant z-50 md:hidden overflow-y-auto no-scrollbar"
            >
              <div className="flex justify-end p-3">
                <button
                  onClick={() => setMobileOpen(false)}
                  aria-label="Close navigation menu"
                  className="p-2 rounded-lg text-secondary hover:bg-surface-container transition-colors"
                >
                  <X size={20} />
                </button>
              </div>
              {sidebarContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
