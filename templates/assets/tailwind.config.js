/** @type {import('tailwindcss').Config} */

import daisyui from "daisyui"
import animations from '@midudev/tailwind-animations'
import theme from "@midudev/tailwind-animations/src/theme"

module.exports = {
  content: ['../../templates/speedy_app/**/*.html'],
  theme: {
    extend: {
      fontFamily: {
        'title': ['"Gobold"', "sans-serif"],
        'text': ['"Roboto"', "sans-serif"],
      }
    },
  },
  plugins: [daisyui, animations, theme],
  daisyui: {
    themes: ['light', 'dark',],
  }
}