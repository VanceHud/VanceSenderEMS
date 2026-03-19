/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/web/**/*.html",
    "./app/web/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        background: '#000000',
        panel: '#050505',
        surface: 'rgba(20, 20, 20, 0.4)',
        amber: {
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
        }
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
      },
      boxShadow: {
        'glass': '0 24px 60px -12px rgba(0, 0, 0, 1)',
        'float': '0 30px 60px -10px rgba(0, 0, 0, 0.8), inset 0 1px 0 rgba(255, 255, 255, 0.08)'
      }
    },
  },
  plugins: [],
}
