/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        amazon_blue: {
          light: "#232F3E", // Lighter Amazon blue for secondary nav if needed
          DEFAULT: "#131921", // Main Amazon blue
        },
      },
    },
  },
  plugins: [],
}