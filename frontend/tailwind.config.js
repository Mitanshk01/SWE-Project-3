module.exports = {
  mode: 'jit',
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'brand-blue': '#0070f3',
        'light-blue': '#e0f2fe',
        'dark-blue': '#1e40af',
      },
      boxShadow: {
        'strong': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)'
      }
    },
  },
  plugins: [],
};