import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx,mdx}"],
  theme: {
    colors: {
      white: "#fdfef8", // Lch(0.995, 0.03, 2)
      black: "#10110b", // Lch(0.05, 0.03, 2)
      gras: {
        superlight: "#c2e053", // Lch(0.85, 0.7, 2)
        light: "#a0bf31", // Lch(0.73, 0.7, 2)
        semilight: "#7e9e00", // Lch(0.61, 0.7, 2)
        DEFAULT: "#688300", // Lch(0.51, 0.61, 2)
        semidark: "#526800", // Lch(0.41, 0.52, 2)
        dark: "#3d4f00", // Lch(0.31, 0.43, 2)
      },
      forest: {
        superlight: "#d0d9a0", // Lch(0.85, 0.3, 2)
        light: "#afb880", // Lch(0.73, 0.3, 2)
        semilight: "#8e9862", // Lch(0.61, 0.3, 2)
        DEFAULT: "#747e4a", // Lch(0.51, 0.3, 2)
        semidark: "#5b6532", // Lch(0.41, 0.3, 2)
        dark: "#434d1c", // Lch(0.31, 0.3, 2)
        superdark: "#293401", // Lch(0.2, 0.3, 2)
      },
      "pale-forest": {
        superlight: "#d3d6c3", // Lch(0.85, 0.1, 2)
        light: "#b2b4a2", // Lch(0.73, 0.1, 2)
        semilight: "#929483", // Lch(0.61, 0.1, 2)
        DEFAULT: "#787b69", // Lch(0.51, 0.1, 2)
        semidark: "#5f6251", // Lch(0.41, 0.1, 2)
        dark: "#484a3a", // Lch(0.31, 0.1, 2)
        superdark: "#2f3122", // Lch(0.2, 0.1, 2)
      },
      ash: {
        superlight: "#d4d4cf", // Lch(0.85, 0.03, 2)
        light: "#b3b3ae", // Lch(0.73, 0.03, 2)
        semilight: "#93938e", // Lch(0.61, 0.03, 2)
        DEFAULT: "#797974", // Lch(0.51, 0.03, 2)
        semidark: "#60615c", // Lch(0.41, 0.03, 2)
        dark: "#484944", // Lch(0.31, 0.03, 2)
        superdark: "#30302c", // Lch(0.2, 0.03, 2)
      },
      sun: {
        light: "#ff9957", // Lch(0.73, 0.6, 1)
        semilight: "#e47627", // Lch(0.61, 0.7, 1)
        DEFAULT: "#c25a03", // Lch(0.51, 0.7, 1)
        semidark: "#9e4700", // Lch(0.41, 0.61, 1)
        dark: "#793500", // Lch(0.31, 0.5, 1)
      },
      sand: {
        superlight: "#ffc8a5", // Lch(0.85, 0.3, 1)
        light: "#dea785", // Lch(0.73, 0.3, 1)
        semilight: "#bc8767", // Lch(0.61, 0.3, 1)
        DEFAULT: "#a06e4f", // Lch(0.51, 0.3, 1)
        semidark: "#845537", // Lch(0.41, 0.3, 1)
        dark: "#693e21", // Lch(0.31, 0.3, 1)
        superdark: "#4d2509", // Lch(0.2, 0.3, 1)
      },
      "pale-sand": {
        superlight: "#e5d0c4", // Lch(0.85, 0.1, 1)
        light: "#c3afa4", // Lch(0.73, 0.1, 1)
        semilight: "#a28f84", // Lch(0.61, 0.1, 1)
        DEFAULT: "#88756b", // Lch(0.51, 0.1, 1)
        semidark: "#6e5d53", // Lch(0.41, 0.1, 1)
        dark: "#56453c", // Lch(0.31, 0.1, 1)
        superdark: "#3c2d24", // Lch(0.2, 0.1, 1)
      },
      sky: {
        superlight: "#82e3f6", // Lch(0.85, 0.3, -2.5)
        light: "#5cc0d2", // Lch(0.73, 0.3, -2.5)
        semilight: "#37a1b2", // Lch(0.61, 0.3, -2.5)
        DEFAULT: "#008596", // Lch(0.51, 0.3, -2.5)
        semidark: "#006b7c", // Lch(0.41, 0.3, -2.5)
        dark: "#005363", // Lch(0.31, 0.3, -2.5)
        superdark: "#003a4a", // Lch(0.2, 0.3, -2.5)
      },
      "pale-sky": {
        superlight: "#bedae0", // Lch(0.85, 0.1, -2.5)
        light: "#9cb7bd", // Lch(0.73, 0.1, -2.5)
        semilight: "#7e989e", // Lch(0.61, 0.1, -2.5)
        DEFAULT: "#637d82", // Lch(0.51, 0.1, -2.5)
        semidark: "#4a6469", // Lch(0.41, 0.1, -2.5)
        dark: "#334c51", // Lch(0.31, 0.1, -2.5)
        superdark: "#1b3438", // Lch(0.2, 0.1, -2.5),
      },
      dawn: {
        superlight: "#ffc1d6", // Lch(0.85, 0.3, 0)
        light: "#e79eb3", // Lch(0.73, 0.3, 0)
        semilight: "#c67f95", // Lch(0.61, 0.3, 0)
        DEFAULT: "#a86479", // Lch(0.51, 0.3, 0)
        semidark: "#8c4b60", // Lch(0.41, 0.3, 0)
        dark: "#723349", // Lch(0.31, 0.3, 0)
        superdark: "#561a31", // Lch(0.2, 0.3, 0)
      },
      "pale-dawn": {
        superlight: "#e8cfd5", // Lch(0.85, 0.1, 0)
        light: "#c5acb3", // Lch(0.73, 0.1, 0)
        semilight: "#a58e94", // Lch(0.61, 0.1, 0)
        DEFAULT: "#897278", // Lch(0.51, 0.1, 0)
        semidark: "#705a60", // Lch(0.41, 0.1, 0)
        dark: "#574248", // Lch(0.31, 0.1, 0)
        superdark: "#3e2b30", // Lch(0.2, 0.1, 0)
      },
    },
    fontFamily: {
      sans: ["Laila", "sans-serif"],
      display: ["Cantora One", "sans-serif"],
    },
    fontSize: {
      xs: "0.64rem",
      sm: "0.8rem",
      base: "1rem",
      lg: "1.25rem",
      xl: "1.5625rem",
      "2xl": "2rem",
      "3xl": "2.5rem",
      "4xl": "3rem",
    },
    fontWeight: {
      light: "300",
      normal: "400",
      medium: "500",
      semibold: "500",
      bold: "700",
    },
    borderRadius: {},
    boxShadow: {},
    screens: {},
    extend: {},
  },
  plugins: [],
} satisfies Config;
