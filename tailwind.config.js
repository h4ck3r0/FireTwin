/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/app/**/*.{js,ts,jsx,tsx}',
    './src/components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#0f1419',
          sidebar: '#1a1f2e',
          card: '#252d3d',
          border: '#3a4556',
          text: '#e4e6eb',
        },
        status: {
          ready: '#10b981',
          warning: '#f59e0b',
          critical: '#ef4444',
          info: '#3b82f6',
        }
      },
      animation: {
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        gauge: 'gauge 0.8s ease-in-out',
      },
      keyframes: {
        gauge: {
          '0%': { transform: 'rotate(-90deg)' },
          '100%': { transform: 'rotate(var(--gauge-rotation))' },
        }
      }
    },
  },
  plugins: [],
}
