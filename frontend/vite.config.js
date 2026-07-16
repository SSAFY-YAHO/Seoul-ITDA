import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '..', '')
  const apiBaseUrl = (env.VITE_API_BASE_URL || '').trim()

  if (mode === 'android' && (!apiBaseUrl || /localhost|127\.0\.0\.1/.test(apiBaseUrl))) {
    throw new Error('Android 빌드에는 공개 HTTPS VITE_API_BASE_URL이 필요합니다.')
  }

  return {
    plugins: [vue()],
    envDir: '..',
    server: {
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
  }
})
