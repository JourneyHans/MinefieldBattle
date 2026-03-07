/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'game-bg': '#1a1a2e',
        'game-panel': '#16213e',
        'game-accent': '#0f3460',
        'game-highlight': '#e94560',
        'game-text': '#f1f1f1',
        'game-secondary': '#a2a8d3',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
