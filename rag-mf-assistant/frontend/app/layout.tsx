import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Mutual Fund Facts Assistant | HDFC MF",
  description:
    "Get factual information about HDFC Mutual Fund schemes — expense ratios, exit loads, SIP minimums, and more. Facts-only. No investment advice.",
  keywords: [
    "HDFC Mutual Fund",
    "mutual fund facts",
    "expense ratio",
    "exit load",
    "SIP",
    "NAV",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="h-full bg-background font-sans antialiased text-on-surface">
        {children}
      </body>
    </html>
  );
}
