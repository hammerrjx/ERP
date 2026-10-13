import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '')
  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port: mode === 'cutoff' ? 5186 : 5173,
      strictPort: true,
      allowedHosts: true,
      proxy: { '/api': { target: mode === 'cutoff' ? 'http://127.0.0.1:8021' : env.VITE_API_TARGET || 'http://127.0.0.1:8000', changeOrigin: true } },
    },
  }
})
