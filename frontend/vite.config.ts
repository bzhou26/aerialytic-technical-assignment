import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://backend-service:8001', // Docker Compose service name and port
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
