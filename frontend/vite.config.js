import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://localhost:8000',
      '/users': 'http://localhost:8000',
      '/certificates': 'http://localhost:8000',
      '/subscriptions': 'http://localhost:8000',
      '/database': 'http://localhost:8000',
      '/logs': 'http://localhost:8000',
    },
    historyApiFallback: true
  }
})