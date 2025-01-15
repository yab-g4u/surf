import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0b0f14",
        panel: "#101923",
        panelAlt: "#132030",
        accent: "#4dd8ff",
        accentAlt: "#ffb454",
        text: "#d7e3f0",
        muted: "#8ba0b6"
      },
      boxShadow: {
        neon: "0 0 0 1px rgba(77,216,255,0.24), 0 0 24px rgba(77,216,255,0.1)"
      }
    }
  },
  plugins: []
};

export default config;
