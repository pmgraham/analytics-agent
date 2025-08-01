import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/run_sse': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        ws: true,
      },
      '/apps': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
