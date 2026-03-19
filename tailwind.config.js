/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/web/**/*.html",
    "./app/web/**/*.js"
  ],
  theme: {
    fontFamily: {
      sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', '"SF Pro Display"', '"Segoe UI"', 'Roboto', 'Helvetica', 'sans-serif'],
    },
    extend: {
      colors: {
        background: '#000000',
        panel: 'rgba(28, 28, 30, 0.45)', // macOS dark material
        surface: 'rgba(255, 255, 255, 0.08)',
        borderglass: 'rgba(255, 255, 255, 0.1)',
        amber: {
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
        }
      },
      borderRadius: {
        'mac': '22px',
        'mac-inner': '14px',
        '2xl': '1rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
        '5xl': '2.5rem',
      },
      backdropBlur: {
        '2xl': '40px',
        '3xl': '64px',
        'mac': '80px',
      },
      boxShadow: {
        'glass': '0 24px 60px -12px rgba(0, 0, 0, 0.8), inset 0 1px 0 rgba(255, 255, 255, 0.08)',
        'mac': '0 0 0 1px rgba(255,255,255,0.08), 0 20px 40px -10px rgba(0,0,0,0.8), inset 0 1px 0 rgba(255,255,255,0.15)',
        'float': '0 30px 60px -10px rgba(0, 0, 0, 0.8), inset 0 1px 0 rgba(255, 255, 255, 0.08)'
      },
      animation: {
        'spring-in': 'springScale 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards',
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'slide-up': 'slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards',
      },
      keyframes: {
        springScale: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        }
      }
    },
  },
  plugins: [],
}
