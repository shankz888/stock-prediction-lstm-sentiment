/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        fin: {
          bg: '#0B0F19',
          card: '#111827',
          cardBorder: '#1F2937',
          accent: '#3B82F6',
          green: '#10B981',
          red: '#EF4444',
          yellow: '#F59E0B',
          purple: '#8B5CF6'
        }
      }
    },
  },
  plugins: [],
}
