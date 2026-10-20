/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        saffron: {
          50: '#fff8ed',
          100: '#ffefd5',
          200: '#ffdcaa',
          300: '#ffc474',
          400: '#ffa03c',
          500: '#ff8016',
          600: '#f0610c',
          700: '#c7460c',
          800: '#9e3812',
          900: '#7f3012',
        },
        civic: {
          50: '#f0f9f4',
          100: '#dcf2e4',
          200: '#bce4cb',
          300: '#8bcfa7',
          400: '#57b37e',
          500: '#339760',
          600: '#24784b',
          700: '#1e5f3d',
          800: '#1b4c32',
          900: '#173f29',
        },
      },
      fontFamily: {
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
        display: ['"Inter"', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
};
