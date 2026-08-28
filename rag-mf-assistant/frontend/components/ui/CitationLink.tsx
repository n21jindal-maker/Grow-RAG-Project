"use client";

import { ExternalLink } from "lucide-react";

interface CitationLinkProps {
  url: string;
}

export function CitationLink({ url }: CitationLinkProps) {
  let hostname = url;
  try {
    hostname = new URL(url).hostname.replace(/^www\./, "");
  } catch {
    // fallback to raw url if parsing fails
  }

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-1 text-label-md text-primary hover:underline transition-colors"
      aria-label={`Source: ${hostname} (opens in new tab)`}
    >
      <span>Source: {hostname}</span>
      <ExternalLink size={11} strokeWidth={2} aria-hidden />
    </a>
  );
}
