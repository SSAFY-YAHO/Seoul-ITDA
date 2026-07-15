<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import brandMark from "../../assets/mascot.png";
import { fetchHealth } from "../../api/health";

const route = useRoute();
const router = useRouter();
const healthStatus = ref("checking");
const healthEnvironment = ref("");

const healthLabel = computed(() => {
  if (healthStatus.value === "ok") return "API 정상";
  if (healthStatus.value === "error") return "API 확인 필요";
  return "API 확인 중";
});

function isActive(path) {
  return route.path === path;
}

async function loadHealth() {
  healthStatus.value = "checking";
  try {
    const data = await fetchHealth();
    healthStatus.value = data?.status === "ok" ? "ok" : "error";
    healthEnvironment.value = data?.environment || "";
  } catch (_error) {
    healthStatus.value = "error";
    healthEnvironment.value = "";
  }
}

onMounted(() => {
  loadHealth();
});
</script>

<template>
  <header class="app-header">
    <div class="container app-header__inner">
      <button class="brand" type="button" @click="router.push('/')">
        <img class="brand__icon" :src="brandMark" alt="서울잇다 해치 아이콘" />
        <div class="brand__wordmark">
          <strong>SEOUL ITDA</strong>
          <span>서울을 잇는 여행</span>
        </div>
      </button>
      <span class="health-chip" :class="`health-chip--${healthStatus}`">
        {{ healthLabel }}
        <small v-if="healthEnvironment">{{ healthEnvironment }}</small>
      </span>
      <nav class="nav-links" aria-label="메인 메뉴">
        <button
          class="nav-link"
          type="button"
          :class="{ 'nav-link--active': isActive('/') }"
          @click="router.push('/')"
        >
          홈
        </button>
        <button
          class="nav-link"
          type="button"
          :class="{
            'nav-link--active':
              isActive('/festivals') || route.path.startsWith('/festivals'),
          }"
          @click="router.push('/festivals')"
        >
          축제 캘린더
        </button>
        <button
          class="nav-link"
          type="button"
          :class="{
            'nav-link--active':
              isActive('/posts') || route.path.startsWith('/posts'),
          }"
          @click="router.push('/posts')"
        >
          커뮤니티
        </button>
      </nav>
    </div>
  </header>
</template>
