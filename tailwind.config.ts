import { Config } from "tailwindcss";
import { fontFamily } from "tailwindcss/defaultTheme";

export default {
  content: ["./src/**/*.tsx"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-geist-sans)", ...fontFamily.sans],
      },
      colors: {
        primary: {
          blue: "#4F46E5",
          purple: "#9333EA",
        },
      },
      backgroundImage: {
        "gradient-primary": "linear-gradient(to right, #4F46E5, #9333EA)",
      },
    },
  },
  plugins: [],
} satisfies Config;