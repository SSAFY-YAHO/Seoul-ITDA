import { createApp } from 'vue'
import './styles/variables.css'
import './styles/global.css'
import App from './App.vue'
import router from './router'
import { Capacitor } from '@capacitor/core'

createApp(App).use(router).mount('#app')

if (import.meta.env.PROD && !Capacitor.isNativePlatform() && 'serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {
      // 서비스 워커 등록에 실패해도 일반 웹 사용은 계속 가능합니다.
    })
  })
}
