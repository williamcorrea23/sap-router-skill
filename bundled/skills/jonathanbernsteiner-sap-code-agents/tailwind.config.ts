// Tailwind CSS configuration — content globs and the warm-minimal theme.
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["DM Sans", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      colors: {
        surface: "#FAF8F5",
        // Main brand / accent color.
        accent: "#F04E0D",
        // Darker orange for pressed states and small accent text (AA contrast).
        "accent-deep": "#CC420B",
        // Near-black used for the sidebar rail, tooltips, primary emphasis.
        ink: "#171412",
        // Warm cream tint for subtle brand-tinted surfaces.
        cream: "#FCEDE4",
      },
    },
  },
  plugins: [],
};

export default config;
