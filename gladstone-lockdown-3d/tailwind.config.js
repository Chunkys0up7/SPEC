/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['Fraunces', 'serif'],
        sans: ['Spline Sans', 'system-ui', 'sans-serif'],
      },
      colors: {
        ink: '#231f4a',
        ink2: '#4a4775',
        paper: '#fbf7ff',
        paper2: '#f1ecfb',
        line: '#e6e0f5',
        forest: '#5b5bd6',
        gold: '#e0337a',
        gold2: '#ffc53d',
        rust: '#f0473f',
        good: '#19b36b',
        bad: '#f0473f',
        sage: '#7c73b8',
        grape: '#7c5cff',
        sky: '#22b8d6',
        lime: '#7cc242',
        c1: '#9ed863',
        c2: '#46d3ec',
        c3: '#ff5a9e',
        c4: '#a88bff',
      },
    },
  },
  plugins: [],
};
