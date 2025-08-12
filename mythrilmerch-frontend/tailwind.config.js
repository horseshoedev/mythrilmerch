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
        'sans': ['IM Fell English', 'serif'], // Override default sans
      },
      colors: {
        amazonBlue: '#131921', // Example: Header background
        amazonOrange: '#FF9900', // Example: Button color
        amazonLightBlue: '#232F3E', // Example: Sub-header
        amazonGreen: '#007185', // Example: Link hover
        gray: {
          100: '#F5F5F5',
          200: '#EAEAEA',
          // ... more shades based on Amazon's UI
          800: '#333333',
        },
        // Add other specific Amazon colors
      },
      spacing: {
        // If Amazon uses very specific, non-standard spacing, define them here.
        '72': '18rem',
        '84': '21rem',
        '96': '24rem',
        '128': '32rem',
        // ... based on your analysis
      },
      boxShadow: {
        'amazon': '0 0 0 1px rgba(0,0,0,.1) inset', // Example for input fields
        'amazon-hover': '0 0 0 1px rgba(0,0,0,.2) inset', // Example for input fields
        // Custom shadows for cards or elevated elements
      },
      borderRadius: {
        'amazon-sm': '2px', // Very subtle
        'amazon-md': '3px',
        'amazon-lg': '4px', // For buttons, etc.
      },
      // You might also extend other properties like `minWidth`, `maxWidth`, `height`, `zIndex` if Amazon's layout demands specific values not covered by defaults.
    },
  },
  plugins: [],
}