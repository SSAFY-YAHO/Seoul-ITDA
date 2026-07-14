<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import brandMark from "../assets/mascot.png";
import { fetchLocations } from "../api/locations";
import { fetchFestivals } from "../api/festivals";
import { parseFestivalDateRange } from "../utils/festivalDate";

const router = useRouter();
const locations = ref([]);
const loading = ref(true);
const error = ref("");
const activeGuide = ref("");
const selectedMapLocation = ref(null);
const festivalItems = ref([]);
const festivalLoading = ref(false);
const festivalError = ref("");
const viewportWidth = ref(typeof window !== "undefined" ? window.innerWidth : 1200);
const locationSlideIndex = ref(0);

const guideCards = [
  {
    key: "tour",
    title: "관광지 먼저 보기",
    description: "도심 속 명소와 산책하기 좋은 동선을 말랑하게 먼저 확인합니다.",
    buttonLabel: "바로 열기",
  },
  {
    key: "festival",
    title: "축제 일정 확인",
    description: "이번 달 서울 축제를 날짜 순서대로 귀엽게 살펴봅니다.",
    buttonLabel: "바로 열기",
  },
];

const recommendedLocations = computed(() => locations.value);
const cardsPerView = computed(() => {
  if (viewportWidth.value < 640) return 1;
  if (viewportWidth.value < 920) return 2;
  return 3;
});
const maxLocationSlideIndex = computed(() =>
  Math.max(0, recommendedLocations.value.length - cardsPerView.value),
);
const visibleLocations = computed(() =>
  recommendedLocations.value.slice(
    locationSlideIndex.value,
    locationSlideIndex.value + cardsPerView.value,
  ),
);

const activeGuideTitle = computed(() => {
  if (activeGuide.value === "tour") return "관광지 먼저 보기";
  if (activeGuide.value === "festival") return "가장 가까운 축제 일정";
  return "빠른 안내";
});

const selectedLocationQuery = computed(() => {
  if (!selectedMapLocation.value) return "";

  return [
    selectedMapLocation.value.name || selectedMapLocation.value.title || "",
    formatLocationAddress(selectedMapLocation.value),
  ]
    .filter(Boolean)
    .join(" ");
});

const mapEmbedUrl = computed(() => {
  if (!selectedLocationQuery.value) return "";

  return `https://maps.google.com/maps?q=${encodeURIComponent(selectedLocationQuery.value)}&z=14&output=embed`;
});

const naverMapUrl = computed(() => {
  if (!selectedLocationQuery.value) return "";

  return `https://map.naver.com/p/search/${encodeURIComponent(selectedLocationQuery.value)}`;
});

const nearestFestivals = computed(() => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  return festivalItems.value
    .map((festival) => ({
      festival,
      dateRange: parseFestivalDateRange(festival),
    }))
    .filter(({ dateRange }) => dateRange && dateRange.end >= today)
    .sort((a, b) => {
      const aGap = a.dateRange.start > today ? a.dateRange.start - today : 0;
      const bGap = b.dateRange.start > today ? b.dateRange.start - today : 0;
      if (aGap !== bGap) return aGap - bGap;
      return a.dateRange.start - b.dateRange.start;
    })
    .slice(0, 5);
});

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

function formatFestivalPeriod(festival) {
  const parsed = parseFestivalDateRange(festival);
  if (!parsed) return "기간 정보 미정";
  const start = parsed.start.toLocaleDateString("ko-KR", {
    month: "long",
    day: "numeric",
  });
  const end = parsed.end.toLocaleDateString("ko-KR", {
    month: "long",
    day: "numeric",
  });
  return `${start} ~ ${end}`;
}

function getFestivalTitle(festival) {
  return festival.title || festival.name || festival.festivalName || "축제";
}

function getFestivalPlace(festival) {
  return festival.place || festival.venue || festival.location || "장소 정보 미정";
}

function updateViewportWidth() {
  viewportWidth.value = window.innerWidth;
}

function prevLocationPage() {
  locationSlideIndex.value = Math.max(0, locationSlideIndex.value - 1);
}

function nextLocationPage() {
  locationSlideIndex.value = Math.min(
    maxLocationSlideIndex.value,
    locationSlideIndex.value + 1,
  );
}

function selectMapLocation(location) {
  selectedMapLocation.value = location;
}

async function loadFestivalsForGuide() {
  festivalLoading.value = true;
  festivalError.value = "";

  try {
    const data = await fetchFestivals();
    festivalItems.value = Array.isArray(data) ? data : data?.items || [];
  } catch (err) {
    festivalError.value = err.message || "축제 정보를 불러오지 못했습니다.";
    festivalItems.value = [];
  } finally {
    festivalLoading.value = false;
  }
}

async function openGuide(type) {
  activeGuide.value = type;

  if (type === "tour" && !selectedMapLocation.value && recommendedLocations.value.length > 0) {
    selectedMapLocation.value = recommendedLocations.value[0];
  }

  if (type === "festival" && festivalItems.value.length === 0) {
    await loadFestivalsForGuide();
  }
}

function closeGuide() {
  activeGuide.value = "";
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
  window.addEventListener("resize", updateViewportWidth);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", updateViewportWidth);
});

watch([recommendedLocations, cardsPerView], () => {
  if (locationSlideIndex.value > maxLocationSlideIndex.value) {
    locationSlideIndex.value = maxLocationSlideIndex.value;
  }
  if (!selectedMapLocation.value && recommendedLocations.value.length > 0) {
    selectedMapLocation.value = recommendedLocations.value[0];
  }
});
</script>

<template>
  <div class="page-shell home-page">
    <section class="hero-section section-card home-hero">
      <div class="hero-copy">
        <span class="badge badge--blue">서울잇다 · 도시 정보 허브</span>
        <h1>서울을 처음 보는 사람도 금방 길을 찾게</h1>
        <p>
          서울잇다는 서울 관광 정보와 축제 일정, 그리고 사용자 후기를 함께
          모아 빠르게 확인할 수 있는 통합 안내 사이트입니다.
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
          <button class="btn btn--ghost btn--small" type="button" @click="openGuide(card.key)">
            {{ card.buttonLabel }}
          </button>
        </article>
      </div>
    </section>

    <section class="section-card section-block">
      <div class="section-heading">
        <div>
          <p class="section-label">추천 장소</p>
          <h2>지금 둘러볼 만한 서울 정보</h2>
          <p class="page-subtitle">실제 데이터가 있으면 바로 카드로, 없으면 안내 문구로 보여줍니다.</p>
        </div>
        <div class="inline-actions">
          <button class="btn btn--ghost" type="button" @click="loadLocations">
            새로고침
          </button>
          <button
            class="btn btn--secondary btn--small"
            type="button"
            :disabled="locationSlideIndex === 0"
            @click="prevLocationPage"
          >
            이전
          </button>
          <button
            class="btn btn--secondary btn--small"
            type="button"
            :disabled="locationSlideIndex >= maxLocationSlideIndex"
            @click="nextLocationPage"
          >
            다음
          </button>
        </div>
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
      <div v-else class="card-list home-location-track">
        <article
          v-for="location in visibleLocations"
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

    <div v-if="activeGuide" class="modal-backdrop" @click.self="closeGuide">
      <section class="section-card modal-card home-guide-modal">
        <div class="modal-card__header">
          <div>
            <p class="section-label">빠른 안내</p>
            <h2>{{ activeGuideTitle }}</h2>
          </div>
          <button class="btn btn--ghost btn--small" type="button" @click="closeGuide">
            닫기
          </button>
        </div>

        <div class="modal-card__body">
          <div v-if="activeGuide === 'tour'">
            <div v-if="loading" class="loading-state">
              <strong>관광지 목록을 준비하는 중입니다.</strong>
              <p>잠시만 기다려 주세요.</p>
            </div>
            <div v-else-if="recommendedLocations.length === 0" class="empty-state">
              <strong>표시할 관광지 데이터가 없습니다.</strong>
              <p>잠시 후 다시 시도해 주세요.</p>
            </div>
            <div v-else class="guide-map-layout">
              <div class="guide-map-wrap">
                <iframe
                  v-if="mapEmbedUrl"
                  class="guide-map-frame"
                  :src="mapEmbedUrl"
                  title="관광지 지도"
                  loading="lazy"
                  referrerpolicy="no-referrer-when-downgrade"
                />
                <a
                  v-if="naverMapUrl"
                  class="btn btn--primary guide-map-link"
                  :href="naverMapUrl"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  네이버 지도에서 열기
                </a>
              </div>
              <div class="guide-location-list">
                <button
                  v-for="location in recommendedLocations.slice(0, 8)"
                  :key="location.id || location.name"
                  class="guide-location-item"
                  :class="{ 'guide-location-item--active': selectedMapLocation?.id === location.id }"
                  type="button"
                  @click="selectMapLocation(location)"
                >
                  <strong>{{ location.name || location.title || "이름 미정" }}</strong>
                  <span>{{ formatLocationAddress(location) }}</span>
                </button>
              </div>
            </div>
          </div>

          <div v-else-if="activeGuide === 'festival'">
            <div v-if="festivalLoading" class="loading-state">
              <strong>가장 가까운 축제를 찾는 중입니다.</strong>
              <p>잠시만 기다려 주세요.</p>
            </div>
            <div v-else-if="festivalError" class="error-state">
              <strong>축제 정보를 불러오지 못했습니다.</strong>
              <p>{{ festivalError }}</p>
            </div>
            <div v-else-if="nearestFestivals.length === 0" class="empty-state">
              <strong>현재 기준으로 표시할 일정이 없습니다.</strong>
              <p>필터를 넓혀 전체 축제 캘린더에서 확인해 주세요.</p>
            </div>
            <div v-else class="guide-festival-list">
              <article
                v-for="item in nearestFestivals"
                :key="item.festival.id || getFestivalTitle(item.festival)"
                class="detail-card detail-card--compact"
              >
                <span class="badge badge--yellow">가까운 일정</span>
                <h3>{{ getFestivalTitle(item.festival) }}</h3>
                <p>{{ formatFestivalPeriod(item.festival) }}</p>
                <p class="helper-text">{{ getFestivalPlace(item.festival) }}</p>
              </article>
            </div>
          </div>
        </div>
      </section>
    </div>

  </div>
</template>
