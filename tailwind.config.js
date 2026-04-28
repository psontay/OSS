/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",        // Thư mục templates tổng
    "./OSS/templates/**/*.html",    // Thư mục templates trong app OSS
    "./OSS/controller/**/*.py",     // Quét cả file python nếu ông dùng class trong đó
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}