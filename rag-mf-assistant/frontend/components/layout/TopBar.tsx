"use client";

import { Info, Bell, UserCircle } from "lucide-react";

export function TopBar() {
  return (
    <header className="glass-header sticky top-0 z-30 border-b border-surface-variant">
      {/* Disclaimer strip */}
      <div className="flex items-center justify-center gap-2 px-6 py-2 bg-surface-container-low text-on-surface-variant text-label-md font-medium border-b border-surface-variant">
        <Info size={14} className="shrink-0 text-primary" aria-hidden />
        <span>Facts-only. No investment advice.</span>
      </div>

      {/* Action icons row */}
      <div className="flex items-center justify-end gap-2 px-6 py-2">
        <button
          aria-label="Account"
          className="p-1.5 rounded-full text-secondary hover:text-primary hover:bg-surface-container transition-colors"
        >
          <UserCircle size={22} strokeWidth={1.75} />
        </button>
        <button
          aria-label="Notifications"
          className="p-1.5 rounded-full text-secondary hover:text-primary hover:bg-surface-container transition-colors"
        >
          <Bell size={22} strokeWidth={1.75} />
        </button>
      </div>
    </header>
  );
}
