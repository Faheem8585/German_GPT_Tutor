import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // German-inspired palette
        german: {
          black: "#000000",
          red: "#DD0000",
          gold: "#FFCE00",
          dark: "#1a1a2e",
        },
        brand: {
          50: "#fdf8ff",
          100: "#f3e8ff",
          200: "#e9d5ff",
          300: "#d8b4fe",
          400: "#c084fc",
          500: "#a855f7",
          600: "#9333ea",
          700: "#7c3aed",
          800: "#6b21a8",
          900: "#581c87",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Playfair Display", "Georgia", "serif"],
      },
      backgroundImage: {
        "german-gradient": "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
        "gold-gradient": "linear-gradient(135deg, #f6d365 0%, #fda085 100%)",
        "brand-gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "hero-gradient": "radial-gradient(ellipse at center, #1a1a2e 0%, #0d0d1a 100%)",
      },
      animation: {
        "float": "float 3s ease-in-out infinite",
        "pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "streak-fire": "streakFire 1s ease-in-out infinite alternate",
        "xp-pop": "xpPop 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)",
        "slide-up": "slideUp 0.3s ease-out",
        "fade-in": "fadeIn 0.4s ease-out",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        streakFire: {
          "0%": { transform: "scale(1)", filter: "hue-rotate(0deg)" },
          "100%": { transform: "scale(1.1)", filter: "hue-rotate(20deg)" },
        },
        xpPop: {
          "0%": { transform: "scale(0) translateY(20px)", opacity: "0" },
          "100%": { transform: "scale(1) translateY(0)", opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(20px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
      },
      boxShadow: {
        "glow-brand": "0 0 20px rgba(168, 85, 247, 0.4)",
        "glow-gold": "0 0 20px rgba(255, 206, 0, 0.4)",
        "glow-green": "0 0 20px rgba(34, 197, 94, 0.4)",
        "card": "0 4px 24px rgba(0, 0, 0, 0.12)",
        "card-hover": "0 8px 40px rgba(0, 0, 0, 0.2)",
      },
    },
  },
  plugins: [],
};

export default config;
