<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import mascot from "../../assets/mascot.png";
import { fetchHealth } from "../../api/health";

const route = useRoute();
const router = useRouter();
const healthStatus = ref("checking");
const mobileOpen = ref(false);

const healthLabel = computed(() => ({ ok: "API 연결", error: "API 점검 필요", checking: "연결 확인 중" }[healthStatus.value]));
const navItems = [
  { label: "서울 정보", path: "/" },
  { label: "축제 캘린더", path: "/festivals" },
  { label: "시민 커뮤니티", path: "/posts" },
];

function active(path) {
  return path === "/" ? route.path === "/" : route.path.startsWith(path);
}

function go(path) {
  mobileOpen.value = false;
  router.push(path);
}

onMounted(async () => {
  try {
    const data = await fetchHealth();
    healthStatus.value = data?.status === "ok" ? "ok" : "error";
  } catch {
    healthStatus.value = "error";
  }
});
</script>

<template>
  <header class="portal-header">
    <div class="portal-topbar">
      <div class="container">
        <span>서울 공공데이터 기반 지역정보 서비스</span>
        <div><span :class="`api-dot api-dot--${healthStatus}`"></span>{{ healthLabel }}</div>
      </div>
    </div>
    <div class="container portal-brand-row">
      <button class="portal-brand" type="button" @click="go('/')">
        <img :src="mascot" alt="서울잇다 마스코트" />
        <span><strong>서울잇다</strong><small>SEOUL LOCAL INFORMATION HUB</small></span>
      </button>
      <div class="portal-utilities">
        <button type="button" @click="go('/posts/new')">경험 공유</button>
        <button class="portal-search-shortcut" type="button" @click="go('/')">통합검색 <b>⌕</b></button>
      </div>
      <button class="mobile-menu" type="button" aria-label="메뉴 열기" @click="mobileOpen = !mobileOpen">☰</button>
    </div>
    <nav class="portal-nav" :class="{ 'portal-nav--open': mobileOpen }" aria-label="주 메뉴">
      <div class="container">
        <button v-for="item in navItems" :key="item.path" type="button" :class="{ active: active(item.path) }" @click="go(item.path)">
          {{ item.label }}
        </button>
        <span class="portal-nav__guide">로그인 없이 누구나 이용할 수 있습니다</span>
      </div>
    </nav>
  </header>
</template>
