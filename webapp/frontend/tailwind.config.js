/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      colors: {
        primary: '#FF6A00',
        bgDark: '#121212',
        bgCard: '#1A1A1A',
        accent: '#2DE282',
        accent2: '#00FFB2',
      },
      borderRadius: {
        'xl': '16px',
        '10': '10px',
        '16': '16px',
        '4': '4px',
      },
      fontSize: {
        base: '0.95rem',
        sm: '0.9rem',
        lg: '1.1rem',
        xl: '1.25rem',
        '2xl': '2rem',
      },
      spacing: {
        '1.5': '0.375rem',
        '2': '0.5rem',
        '4': '1rem',
        '6': '1.5rem',
        '8': '2rem',
      },
      boxShadow: {
        lg: '0 0 12px rgba(0,0,0,0.6)',
      },
      transitionProperty: {
        'width': 'width',
        'colors': 'color,background-color,border-color,text-decoration-color,fill,stroke',
      },
      gap: {
        '1.5': '0.375rem',
        '6': '1.5rem',
      },
    },
  },
  plugins: [],
};
