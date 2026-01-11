/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gold: {
          DEFAULT: '#ffd700',
          dark: '#b8860b',
        },
        'dark-bg': '#0a0e27',
      },
    },
  },
  plugins: [],
}
