import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/accounts/api': {
        target: 'http://web:8000',
        changeOrigin: true,
      },
      '/appointments/api': {
        target: 'http://web:8000',
        changeOrigin: true,
      },
      '/salons/api': {
        target: 'http://web:8000',
        changeOrigin: true,
      },
      '/media': {
        target: 'http://web:8000',
        changeOrigin: true,
      },
      '/static': {
        target: 'http://web:8000',
        changeOrigin: true,
      }
    }
  }
})
