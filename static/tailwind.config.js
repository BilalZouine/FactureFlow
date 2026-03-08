document.addEventListener('load', () => {
  tailwind.config = {
    theme: {
      extend: {
        fontFamily: {
          sans: ['Sora', 'sans-serif'],
          mono: ['JetBrains Mono', 'monospace'],
        },
        colors: {
          surface: '#0f1117',
          panel: '#161b27',
          card: '#1c2333',
          line: '#252d3d',
          muted: '#4a5568',
          subtle: '#6b7a99',
          body: '#a8b3cf',
          bright: '#e2e8f0',
          white: '#f8fafc',
          blue: '#3b82f6',
          'blue-dim': '#1e3a5f',
          green: '#22c55e',
          'green-dim': '#14532d',
          red: '#ef4444',
          'red-dim': '#7f1d1d',
        }
      }
    }
  }
})