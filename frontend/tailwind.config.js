/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'deep-slate': '#0F172A',
        'cloud-gray': '#CBD5E1',
        'soft-mint': '#4ECCA3',
        'muted-amber': '#F59E0B',
        'off-white': '#F8FAFC',
        'muted-text': '#94A3B8',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
