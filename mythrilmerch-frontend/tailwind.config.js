/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      fontFamily: {
        'logo': ['NCL BasefighDemo', 'serif'],
        'text': ['IM Fell English', 'serif'],
        'sans': ['IM Fell English', 'serif'],
      },
      colors: {
        'primary-black': '#1b1b1b', // Main background color
        'secondary-black': '#212121', // Secondary background/card color
        'gray-text': '#7a7a7a', // For secondary text/subheadings
        'light-gray': '#a2a2a2', // For lighter text/links
        'accent-red': '#cc3333', // Primary accent color, used for buttons and links
        'hover-red': '#992626', // A darker red for hover states
        'button-bg': '#cc3333',
        'button-text': '#ffffff',
      },
      spacing: {
        '72': '18rem',
        '84': '21rem',
        '96': '24rem',
        '128': '32rem',
      },
      boxShadow: {
        'ef-card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      },
      borderRadius: {
        'ef-sm': '4px',
        'ef-md': '8px',
      },
    },
  },
  plugins: [],
}