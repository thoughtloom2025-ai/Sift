/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'deep-slate': '#1A1C2E',
        'cloud-gray': '#CBD5E1',
        'soft-mint': '#B2D8C8',
        'muted-amber': '#E2B07E',
        'off-white': '#F8FAFC',
        'muted-text': '#94A3B8',
        'focus-slate': '#1E2235',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      lineHeight: {
        'readable': '1.6',
      },
    },
  },
  plugins: [],
}
