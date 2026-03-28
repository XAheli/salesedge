import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: ["class", '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#FFF8F0",
          100: "#FFEDD5",
          200: "#FED7AA",
          300: "#FDBA74",
          400: "#FB923C",
          500: "#F97316",
          600: "#EA580C",
          700: "#C2410C",
          800: "#9A3412",
          900: "#7C2D12",
        },
        revenue: {
          positive: "#059669",
          "positive-bg": "#D1FAE5",
        },
        caution: {
          DEFAULT: "#D97706",
          bg: "#FEF3C7",
        },
        risk: {
          DEFAULT: "#DC2626",
          bg: "#FEE2E2",
        },
        info: {
          DEFAULT: "#2563EB",
          bg: "#DBEAFE",
        },
        "data-quality": {
          DEFAULT: "#7C3AED",
          bg: "#EDE9FE",
        },
        neutral: {
          DEFAULT: "#6B7280",
          bg: "#F3F4F6",
        },
        surface: {
          background: "var(--surface-background)",
          card: "var(--surface-card)",
          "card-hover": "var(--surface-card-hover)",
          sidebar: "var(--surface-sidebar)",
          "sidebar-text": "var(--surface-sidebar-text)",
          "sidebar-active": "var(--surface-sidebar-active)",
          header: "var(--surface-header)",
        },
        text: {
          primary: "var(--text-primary)",
          secondary: "var(--text-secondary)",
          tertiary: "var(--text-tertiary)",
          inverse: "var(--text-inverse)",
          link: "var(--text-link)",
        },
        chart: {
          1: "var(--chart-1)",
          2: "var(--chart-2)",
          3: "var(--chart-3)",
          4: "var(--chart-4)",
          5: "var(--chart-5)",
          6: "var(--chart-6)",
          7: "var(--chart-7)",
          8: "var(--chart-8)",
        },
      },
      fontFamily: {
        sans: ["Inter", "Noto Sans", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
        display: ["Plus Jakarta Sans", "Inter", "system-ui", "sans-serif"],
      },
      borderRadius: {
        sm: "0.375rem",
        md: "0.5rem",
        lg: "0.75rem",
        xl: "1rem",
      },
      spacing: {
        xs: "0.25rem",
        sm: "0.5rem",
        md: "1rem",
        lg: "1.5rem",
        xl: "2rem",
        "2xl": "3rem",
      },
      boxShadow: {
        sm: "0 1px 2px 0 rgba(28, 25, 23, 0.05)",
        md: "0 4px 6px -1px rgba(28, 25, 23, 0.07), 0 2px 4px -2px rgba(28, 25, 23, 0.05)",
        lg: "0 10px 15px -3px rgba(28, 25, 23, 0.08), 0 4px 6px -4px rgba(28, 25, 23, 0.04)",
        card: "0 1px 3px 0 rgba(28, 25, 23, 0.06), 0 1px 2px -1px rgba(28, 25, 23, 0.06)",
      },
    },
  },
  plugins: [],
};

export default config;
