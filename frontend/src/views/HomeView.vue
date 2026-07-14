<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import brandMark from "../assets/mascot.png";
import { fetchLocations } from "../api/locations";

const router = useRouter();
const locations = ref([]);
const loading = ref(true);
const error = ref("");

const guideCards = [
  {
    title: "관광지 먼저 보기",
    description: "도심 속 명소와 산책하기 좋은 동선을 말랑하게 먼저 확인합니다.",
    action: () => router.push("/festivals"),
  },
  {
    title: "축제 일정 확인",
    description: "이번 달 서울 축제를 날짜 순서대로 귀엽게 살펴봅니다.",
    action: () => router.push("/festivals"),
  },
  {
    title: "커뮤니티 둘러보기",
    description: "익명 글을 통해 실제 방문 경험과 감상을 가볍게 읽습니다.",
    action: () => router.push("/posts"),
  },
];

const heroSignals = [
  { label: "관광·축제·맛집", value: "한 번에 탐색" },
  { label: "지역별 정리", value: "서울 동선 중심" },
  { label: "질문 응답", value: "챗봇 연계" },
];

const summaryCards = computed(() => [
  {
    label: "추천 장소",
    value: `${locations.value.length}개`,
    tone: "badge--blue",
  },
  {
    label: "둘러보기 방식",
    value: "축제 · 장소 · 후기",
    tone: "badge--sky",
  },
  {
    label: "챗봇 활용",
    value: "질문으로 바로 좁히기",
    tone: "badge--ice",
  },
  {
    label: "추천 분위기",
    value: "산책 · 실내 · 야경",
    tone: "badge--slate",
  },
]);

const recommendedLocations = computed(() => locations.value.slice(0, 6));

function getCategoryLabel(category) {
  if (!category) return "정보";
  const map = {
    tourist: "관광지",
    festival: "축제",
    restaurant: "맛집",
    culture: "문화",
    hotel: "숙박",
  };
  return map[category] || category;
}

function getCategoryTone(category) {
  const map = {
    tourist: "badge--blue",
    festival: "badge--sky",
    restaurant: "badge--ice",
    culture: "badge--slate",
    hotel: "badge--ice",
  };
  return map[category] || "badge--blue";
}

function formatLocationAddress(location) {
  return location.address || location.road_address || "주소 정보가 아직 준비되지 않았습니다.";
}

function formatLocationDescription(location) {
  return location.description || location.summary || "설명은 준비 중입니다.";
}

function formatLocationTags(location) {
  if (!location.tags) return "";
  return location.tags
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean)
    .slice(0, 3)
    .join(" · ");
}

async function loadLocations() {
  loading.value = true;
  error.value = "";

  try {
    const data = await fetchLocations();
    locations.value = Array.isArray(data) ? data : data?.items || [];
  } catch (err) {
    error.value = err.message || "서울 정보를 불러오지 못했습니다.";
    locations.value = [];
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadLocations();
});
</script>

<template>
  <div class="page-shell home-page">
    <section class="hero-section section-card home-hero">
      <div class="hero-copy">
        <span class="badge badge--blue">서울잇다 · 도시 정보 허브</span>
        <h1>서울을 처음 보는 사람도 금방 길을 찾게</h1>
        <p>
          관광지, 축제, 맛집, 익명 커뮤니티를 한 화면에서 정리했습니다. 복잡한
          설명보다 먼저 동선이 보이도록 귀엽고 단정하게 배치했습니다.
        </p>
        <div class="hero-actions">
          <button
            class="btn btn--primary"
            type="button"
            @click="router.push('/festivals')"
          >
            축제부터 보기
          </button>
          <button
            class="btn btn--secondary"
            type="button"
            @click="router.push('/posts')"
          >
            커뮤니티 보기
          </button>
        </div>
        <div class="hero-highlights hero-highlights--stacked">
          <div v-for="signal in heroSignals" :key="signal.label" class="highlight-pill">
            <strong>{{ signal.value }}</strong>
            <p>{{ signal.label }}</p>
          </div>
        </div>
      </div>

      <div class="hero-visual hero-visual--stack">
        <div class="hero-panel home-hero-panel">
          <div class="hero-panel__bar">
            <span class="badge badge--sky">오늘의 안내</span>
            <span class="meta-pill">서울을 가볍게 고르는 방법</span>
          </div>
          <div class="hero-panel__stack">
            <article class="hero-panel__card">
              <strong>1. 원하는 지역부터 고르기</strong>
              <p>동네 이름이나 관심 카테고리를 먼저 확인하세요.</p>
            </article>
            <article class="hero-panel__card">
              <strong>2. 축제와 장소를 함께 보기</strong>
              <p>일정과 위치를 나란히 보면 이동 계획이 쉬워집니다.</p>
            </article>
            <article class="hero-panel__card hero-panel__card--wide">
              <strong>3. 궁금한 점은 챗봇에 바로 물어보기</strong>
              <p>검색보다 빠르게, 지금 필요한 정보만 가볍게 확인합니다.</p>
            </article>
          </div>
          <div class="hero-panel__bar">
            <img :src="brandMark" alt="서울잇다 아이콘" />
            <div>
              <strong>서울잇다</strong>
              <p class="helper-text">서울에서 무엇을 할지 빠르게 정리해 주는 여행 안내 화면입니다.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section-card section-block">
      <div class="section-heading">
        <div>
          <p class="section-label">사용 순서</p>
          <h2>처음 방문한 사람을 위한 빠른 안내</h2>
        </div>
      </div>
      <div class="category-grid">
        <article v-for="card in guideCards" :key="card.title" class="category-card">
          <span class="badge badge--ice">가이드</span>
          <h3>{{ card.title }}</h3>
          <p>{{ card.description }}</p>
          <button class="btn btn--ghost btn--small" type="button" @click="card.action">
            바로 열기
          </button>
        </article>
      </div>
    </section>

    <section class="section-card section-block">
      <div class="section-heading">
        <div>
          <p class="section-label">한눈에 보기</p>
          <h2>처음 방문할 때 도움이 되는 정보</h2>
        </div>
      </div>
      <div class="hero-highlights hero-highlights--stacked">
        <div v-for="item in summaryCards" :key="item.label" class="highlight-pill">
          <span :class="['badge', item.tone]">{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
      </div>
    </section>

    <section class="section-card section-block">
      <div class="section-heading">
        <div>
          <p class="section-label">추천 장소</p>
          <h2>지금 둘러볼 만한 서울 정보</h2>
          <p class="page-subtitle">실제 데이터가 있으면 바로 카드로, 없으면 안내 문구로 보여줍니다.</p>
        </div>
        <button class="btn btn--ghost" type="button" @click="loadLocations">
          새로고침
        </button>
      </div>

      <div v-if="loading" class="loading-state">
        <strong>장소 정보를 불러오는 중입니다.</strong>
        <p>조금만 기다리면 서울의 장소 목록이 표시됩니다.</p>
      </div>
      <div v-else-if="error" class="error-state">
        <strong>장소 정보를 불러오지 못했습니다.</strong>
        <p>{{ error }}</p>
        <button class="btn btn--secondary" type="button" @click="loadLocations">
          다시 시도
        </button>
      </div>
      <div v-else-if="recommendedLocations.length === 0" class="empty-state">
        <strong>표시할 장소가 아직 없습니다.</strong>
        <p>지금은 추천 장소를 준비 중입니다. 잠시 후 다시 확인해 주세요.</p>
      </div>
      <div v-else class="card-list">
        <article
          v-for="location in recommendedLocations"
          :key="location.id || location.name"
          class="location-card"
        >
          <div class="location-card__header">
            <span :class="['badge', getCategoryTone(location.category)]">
              {{ getCategoryLabel(location.category) }}
            </span>
            <h3>{{ location.name || location.title || '이름 미정' }}</h3>
          </div>
          <p>{{ formatLocationDescription(location) }}</p>
          <p class="helper-text">{{ formatLocationAddress(location) }}</p>
          <p v-if="formatLocationTags(location)" class="meta-pill">
            {{ formatLocationTags(location) }}
          </p>
        </article>
      </div>
    </section>

    <section class="section-card section-block home-dual-grid">
      <article class="ai-card">
        <div class="ai-card__title">
          <span class="badge badge--sky">서울 일정</span>
          <h3>축제 캘린더로 이동</h3>
        </div>
        <p>
          날짜별로 정리된 축제와 행사를 먼저 확인하면, 서울을 훨씬 편하게 둘러볼
          수 있습니다.
        </p>
        <button class="btn btn--primary btn--small" type="button" @click="router.push('/festivals')">
          축제 페이지 열기
        </button>
      </article>

      <article class="ai-card">
        <div class="ai-card__title">
          <span class="badge badge--ice">커뮤니티</span>
          <h3>익명 글로 현장 느낌 보기</h3>
        </div>
        <p>
          실제로 다녀온 사람들의 짧은 메모를 읽으면 장소 선택이 쉬워집니다.
        </p>
        <button class="btn btn--secondary btn--small" type="button" @click="router.push('/posts')">
          게시글 페이지 열기
        </button>
      </article>
    </section>

  </div>
</template>
