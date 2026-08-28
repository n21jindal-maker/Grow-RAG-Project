"use client";

import { AlertTriangle, ExternalLink } from "lucide-react";

const AMFI_URL =
  "https://www.amfiindia.com/investor-corner/knowledge-center.html";

export function DisclaimerBanner() {
  return (
    <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2.5 text-body-md text-amber-800">
      <AlertTriangle
        size={16}
        className="shrink-0 mt-0.5 text-amber-500"
        aria-hidden
      />
      <div className="flex flex-col gap-0.5">
        <span className="font-medium text-label-md">
          Investment advisory query detected
        </span>
        <span className="text-label-md leading-snug">
          I&apos;m designed to provide only factual information about mutual fund
          schemes. For investment guidance, please consult a SEBI-registered
          advisor or visit{" "}
          <a
            href={AMFI_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-0.5 underline underline-offset-2 font-medium hover:text-amber-900"
            aria-label="AMFI Investor Education (opens in new tab)"
          >
            AMFI Investor Education
            <ExternalLink size={11} aria-hidden />
          </a>
          .
        </span>
      </div>
    </div>
  );
}
