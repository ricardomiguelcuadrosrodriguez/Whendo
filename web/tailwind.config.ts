import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
      },
      colors: {
        // whendo palette
        bg: {
          DEFAULT: "#0A0A0A",
          elevated: "#0F0F0F",
          card: "#121212",
        },
        ink: {
          DEFAULT: "#E5E5E5",       // primary text
          dim: "#8A8A8A",            // secondary
          muted: "#5A5A5A",          // tertiary
        },
        lime: {
          DEFAULT: "#D4F574",       // "neon CRT" accent
          dim: "#9FB955",
        },
        flame: {
          DEFAULT: "#FF8C42",       // warm accent
          dim: "#B36230",
        },
        border: {
          DEFAULT: "#1F1F1F",
          strong: "#2A2A2A",
        },
        success: "#7ED957",
        danger: "#FF5C5C",
        warning: "#FFB627",
      },
      borderRadius: {
        DEFAULT: "2px",
        sm: "1px",
        md: "4px",
        lg: "6px",
      },
      keyframes: {
        blink: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0" },
        },
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "dot-flash": {
          "0%, 100%": { opacity: "0.3" },
          "50%": { opacity: "1" },
        },
      },
      animation: {
        blink: "blink 1s step-end infinite",
        "fade-in": "fade-in 0.3s ease-out",
        "dot-flash": "dot-flash 1.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
