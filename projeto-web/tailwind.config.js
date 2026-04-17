/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        fg: {
          navy: "#0f1e3e",
          "navy-dark": "#0a1530",
          mustard: "#c8a84b",
          "mustard-dark": "#9d832f",
          cream: "#f7f3e8",
        },
      },
      fontFamily: {
        sans: ['"Inter"', "system-ui", "-apple-system", "sans-serif"],
      },
    },
  },
  plugins: [],
};
