/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        'terminal-bg': '#0d1117',
        'terminal-border': '#30363d',
        'terminal-text': '#e6edf3',
        'terminal-primary': '#58a6ff',
        'terminal-secondary': '#7d8590',
        'terminal-accent': '#238636',
        'terminal-warning': '#d29922',
        'terminal-error': '#f85149',
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', 'Courier New', 'monospace'],
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite alternate',
        'type': 'type 3.5s steps(40, end)',
        'blink': 'blink 1s infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%': { 
            'box-shadow': '0 0 5px rgba(88, 166, 255, 0.5)',
            'text-shadow': '0 0 10px rgba(88, 166, 255, 0.5)'
          },
          '100%': { 
            'box-shadow': '0 0 20px rgba(88, 166, 255, 0.9), 0 0 30px rgba(88, 166, 255, 0.6)',
            'text-shadow': '0 0 20px rgba(88, 166, 255, 0.9)'
          }
        },
        'type': {
          'from': { width: '0' },
          'to': { width: '100%' }
        },
        'blink': {
          '0%, 50%': { opacity: '1' },
          '51%, 100%': { opacity: '0' }
        }
      }
    },
  },
  plugins: [],
}