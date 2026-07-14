<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import mascot from '../../assets/mascot.svg'

const route = useRoute()
const router = useRouter()
const isMenuOpen = computed(() => route.name === 'home')

function isActive(path) {
  return route.path === path
}
</script>

<template>
  <header class="app-header">
    <div class="container app-header__inner">
      <button class="brand" type="button" @click="router.push('/')">
        <img :src="mascot" alt="서울잇다 로고" />
        <div>
          <strong>서울잇다</strong>
          <span>서울 로컬 탐색</span>
        </div>
      </button>
      <nav class="nav-links" aria-label="메인 메뉴">
        <button class="nav-link" type="button" :class="{ 'nav-link--active': isActive('/') }" @click="router.push('/')">홈</button>
        <button class="nav-link" type="button" :class="{ 'nav-link--active': isActive('/festivals') || route.path.startsWith('/festivals') }" @click="router.push('/festivals')">축제 캘린더</button>
        <button class="nav-link" type="button" :class="{ 'nav-link--active': isActive('/posts') || route.path.startsWith('/posts') }" @click="router.push('/posts')">커뮤니티</button>
      </nav>
    </div>
  </header>
</template>
