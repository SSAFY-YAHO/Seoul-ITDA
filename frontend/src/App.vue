<template>
  <div class="shell">
    <header class="shell__header">
      <div>
        <p class="eyebrow">LocalHub Seoul</p>
        <h1>서울 관광 정보와 지역 커뮤니티를 한 곳에서 다루는 MVP</h1>
      </div>
      <nav class="shell__nav">
        <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">FastAPI Docs</a>
      </nav>
    </header>

    <main class="shell__main">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
</script>
