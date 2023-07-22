const plugin = require('tailwindcss/plugin');
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      backgroundImage: {
        
      }
    },
  },
  plugins: [
    plugin(function({ addVariant }) {
        addVariant('current', '&.active');
    })
],
}
