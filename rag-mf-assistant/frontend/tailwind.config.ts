import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      // ── Stitch Design System Color Tokens ─────────────────────────────
      colors: {
        primary: "#00d09c",
        "primary-dark": "#006c4f",
        "on-primary": "#ffffff",
        "primary-container": "#00d09c",
        "on-primary-container": "#ffffff",
        "inverse-primary": "#2fe0aa",
        "primary-fixed": "#59fdc5",
        "primary-fixed-dim": "#2fe0aa",
        "on-primary-fixed": "#002116",
        "on-primary-fixed-variant": "#00513b",

        secondary: "#5f5e5e",
        "on-secondary": "#ffffff",
        "secondary-container": "#e5e2e1",
        "on-secondary-container": "#656464",
        "secondary-fixed": "#e5e2e1",
        "secondary-fixed-dim": "#c8c6c5",
        "on-secondary-fixed": "#1c1b1b",
        "on-secondary-fixed-variant": "#474646",

        tertiary: "#5a5d72",
        "on-tertiary": "#ffffff",
        "tertiary-container": "#b4b6ce",
        "on-tertiary-container": "#44475b",
        "tertiary-fixed": "#dfe1fa",
        "tertiary-fixed-dim": "#c3c5dd",
        "on-tertiary-fixed": "#171a2c",
        "on-tertiary-fixed-variant": "#43465a",

        error: "#ba1a1a",
        "on-error": "#ffffff",
        "error-container": "#ffdad6",
        "on-error-container": "#93000a",

        background: "#f8f9fa",
        "on-background": "#191c1d",
        surface: "#f8f9fa",
        "surface-dim": "#d9dadb",
        "surface-bright": "#f8f9fa",
        "surface-container-lowest": "#ffffff",
        "surface-container-low": "#f3f4f5",
        "surface-container": "#edeeef",
        "surface-container-high": "#e7e8e9",
        "surface-container-highest": "#e1e3e4",
        "surface-variant": "#e1e3e4",
        "on-surface": "#191c1d",
        "on-surface-variant": "#3c4a43",
        "inverse-surface": "#2e3132",
        "inverse-on-surface": "#f0f1f2",
        "surface-tint": "#006c4f",

        outline: "#6b7b72",
        "outline-variant": "#bacac1",
      },

      // ── Typography Scale (Stitch) ──────────────────────────────────────
      fontSize: {
        "display-lg": [
          "40px",
          { lineHeight: "48px", letterSpacing: "-0.02em", fontWeight: "700" },
        ],
        "headline-lg": [
          "32px",
          { lineHeight: "40px", letterSpacing: "-0.01em", fontWeight: "600" },
        ],
        "headline-lg-mobile": [
          "28px",
          { lineHeight: "34px", fontWeight: "600" },
        ],
        "headline-md": ["24px", { lineHeight: "32px", fontWeight: "600" }],
        "title-lg": ["20px", { lineHeight: "28px", fontWeight: "600" }],
        "body-lg": ["16px", { lineHeight: "24px", fontWeight: "400" }],
        "body-md": ["14px", { lineHeight: "20px", fontWeight: "400" }],
        "label-md": [
          "12px",
          { lineHeight: "16px", letterSpacing: "0.01em", fontWeight: "500" },
        ],
      },

      // ── Spacing (8px base system) ──────────────────────────────────────
      spacing: {
        xs: "4px",
        sm: "12px",
        base: "8px",
        md: "16px",
        lg: "24px",
        xl: "32px",
        gutter: "24px",
        "margin-mobile": "16px",
        "margin-desktop": "40px",
      },

      // ── Border Radius (Stitch) ─────────────────────────────────────────
      borderRadius: {
        sm: "0.25rem",   // 4px  – checkboxes
        DEFAULT: "0.5rem", // 8px  – inputs
        md: "0.75rem",   // 12px
        lg: "1rem",      // 16px – cards / bubbles
        xl: "1.5rem",    // 24px
        full: "9999px",  // pill – buttons, chips
      },

      // ── Font Family ────────────────────────────────────────────────────
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },

      // ── Box Shadows ────────────────────────────────────────────────────
      boxShadow: {
        card: "0px 4px 12px rgba(0, 0, 0, 0.05)",
        "input-focus": "0px 4px 20px rgba(0, 208, 156, 0.10)",
        toast: "0px 8px 24px rgba(0, 0, 0, 0.12)",
      },
    },
  },
  plugins: [],
};

export default config;
