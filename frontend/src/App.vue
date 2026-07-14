<template>
  <div class="app-shell">
    <AppHeader />
    <main class="app-main">
      <RouterView />
    </main>
    <AppFooter />
    <ChatbotWidget />
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import AppFooter from './components/common/AppFooter.vue'
import AppHeader from './components/common/AppHeader.vue'
import ChatbotWidget from './components/chatbot/ChatbotWidget.vue'
</script>
