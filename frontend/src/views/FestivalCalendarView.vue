<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import FestivalCalendar from "../components/festival/FestivalCalendar.vue";
import FestivalDetailModal from "../components/festival/FestivalDetailModal.vue";
import FestivalFilter from "../components/festival/FestivalFilter.vue";
import { fetchFestivals } from "../api/festivals";
import {
  parseFestivalDateRange,
  toCalendarEvent,
} from "../utils/festivalDate.js";
import brandMark from "../assets/mascot.png";

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const error = ref("");
const festivalItems = ref([]);
const selectedFestival = ref(null);
const viewMode = ref("calendar");
const filters = ref({
  keyword: "",
  month: "",
  status: "",
  region: "",
  category: "",
});
const currentMonth = ref(new Date());
const currentMonthLabel = computed(() =>
  currentMonth.value.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
  }),
);

const availableRegions = computed(() => {
  const regions = new Set();
  festivalItems.value.forEach((festival) => {
    const region = festival.region || festival.area || festival.address || "";
    if (region) regions.add(region);
  });
  return Array.from(regions);
});

const availableCategories = computed(() => {
  const categories = new Set();
  festivalItems.value.forEach((festival) => {
    const category = festival.category || festival.type || "";
    if (category) categories.add(category);
  });
  return Array.from(categories);
});

const hasDatedFestivals = computed(() =>
  filteredFestivals.value.some((festival) => Boolean(parseFestivalDateRange(festival))),
);

const calendarEvents = computed(() => {
  return festivalItems.value
    .map((festival, index) => toCalendarEvent(festival, index))
    .filter(Boolean);
});

function getFestivalStatus(item) {
  const parsed = parseFestivalDateRange(item);
  if (!parsed) return "unknown";
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const end = new Date(parsed.end);
  end.setHours(0, 0, 0, 0);
  if (today < parsed.start) return "upcoming";
  if (today > end) return "ended";
  return "ongoing";
}

const filteredFestivals = computed(() => {
  const keyword = filters.value.keyword.trim().toLowerCase();
  const month = Number(filters.value.month);
  const status = filters.value.status;
  const region = filters.value.region;
  const category = filters.value.category;

  return festivalItems.value.filter((festival) => {
    const title = (
      festival.title ||
      festival.name ||
      festival.festivalName ||
      ""
    ).toLowerCase();
    const description = (
      festival.description ||
      festival.summary ||
      festival.content ||
      ""
    ).toLowerCase();
    const parsed = parseFestivalDateRange(festival);

    if (keyword && !(title.includes(keyword) || description.includes(keyword)))
      return false;
    if (month) {
      if (!parsed || parsed.start.getMonth() + 1 !== month) return false;
    }
    if (status) {
      if (!parsed || getFestivalStatus(festival) !== status) return false;
    }
    if (region) {
      const targetRegion = (
        festival.region ||
        festival.area ||
        festival.address ||
        ""
      ).toLowerCase();
      if (!targetRegion.includes(region.toLowerCase())) return false;
    }
    if (category) {
      const targetCategory = (
        festival.category ||
        festival.type ||
        ""
      ).toLowerCase();
      if (!targetCategory.includes(category.toLowerCase())) return false;
    }

    return true;
  });
});

const visibleEvents = computed(() =>
  filteredFestivals.value
    .map((festival, index) => toCalendarEvent(festival, index))
    .filter(Boolean),
);

const featuredFestivals = computed(() => {
  const sorted = [...filteredFestivals.value].sort((a, b) => {
    const aDate = parseFestivalDateRange(a)?.start;
    const bDate = parseFestivalDateRange(b)?.start;

    if (aDate && bDate) {
      return aDate - bDate;
    }
    if (aDate) return -1;
    if (bDate) return 1;

    return String(a.title || a.name || "").localeCompare(String(b.title || b.name || ""), "ko");
  });
  return sorted.slice(0, 5);
});

function formatPeriod(item) {
  const parsed = parseFestivalDateRange(item);
  if (!parsed) return "기간 정보 미정";
  return `${parsed.start.toLocaleDateString("ko-KR", { month: "short", day: "numeric" })} ~ ${parsed.end.toLocaleDateString("ko-KR", { month: "short", day: "numeric" })}`;
}

function openFestival(festival) {
  selectedFestival.value = {
    title: festival.title || festival.name || festival.festivalName || "축제",
    period: formatPeriod(festival),
    place: festival.place || festival.venue || festival.location || "",
    address: festival.address || "",
    description:
      festival.description || festival.summary || festival.content || "",
    imageUrl:
      festival.imageUrl || festival.image_url || festival.mainImage || "",
    homepageUrl:
      festival.homepageUrl || festival.homepage_url || festival.url || "",
    phone: festival.phone || festival.contact || "",
    category: festival.category || festival.type || "",
  };
}

async function loadFestivals() {
  loading.value = true;
  error.value = "";
  try {
    const data = await fetchFestivals();
    const items = Array.isArray(data) ? data : data?.items || [];
    festivalItems.value = items;
  } catch (err) {
    error.value = err.message || "축제 정보를 불러오지 못했습니다.";
    festivalItems.value = [];
  } finally {
    loading.value = false;
  }
}

function goToToday() {
  currentMonth.value = new Date();
}

function changeMonth(step) {
  const nextMonth = new Date(
    currentMonth.value.getFullYear(),
    currentMonth.value.getMonth() + step,
    1,
  );
  currentMonth.value = nextMonth;
}

function resetFilters() {
  filters.value = {
    keyword: "",
    month: "",
    status: "",
    region: "",
    category: "",
  };
}

watch(currentMonth, (value) => {
  const target = value.toISOString().slice(0, 10);
  if (route.query?.month !== target) {
    router.replace({ query: { ...route.query, month: target } });
  }
});

onMounted(() => {
  loadFestivals();
  const monthQuery = route.query?.month;
  if (monthQuery) {
    const parsed = new Date(monthQuery);
    if (!Number.isNaN(parsed.getTime())) {
      currentMonth.value = parsed;
    }
  }
});

watch(
  [loading, hasDatedFestivals],
  ([isLoading, hasDates]) => {
    if (!isLoading && !hasDates) {
      viewMode.value = "list";
    }
  },
  { immediate: true },
);
</script>

<template>
  <div class="page-shell">
    <section class="section-card hero-section festival-hero">
      <div class="hero-copy">
        <span class="badge badge--yellow">서울 축제 캘린더</span>
        <h1>이번 달의 서울 축제를 한눈에 확인하세요</h1>
        <p>
          날짜, 지역, 카테고리로 축제를 정리해 두어 처음 보는 사람도 바로
          필요한 일정부터 볼 수 있습니다.
        </p>
        <div class="hero-actions">
          <button class="btn btn--primary" type="button" @click="goToToday">
            오늘로 이동
          </button>
          <button
            class="btn btn--secondary"
            type="button"
            @click="router.push('/')"
          >
            홈으로 돌아가기
          </button>
        </div>
      </div>
      <div class="hero-visual">
        <img :src="brandMark" alt="서울잇다 해치 아이콘" />
      </div>
    </section>

    <FestivalFilter
      :filters="filters"
      :available-regions="availableRegions"
      :available-categories="availableCategories"
      :view-mode="viewMode"
      :current-month-label="currentMonthLabel"
      @update:filters="filters = $event"
      @update:viewMode="viewMode = $event"
      @reset="resetFilters"
    />

    <section v-if="viewMode !== 'list'" class="section-card section-block">
      <div class="section-heading">
        <div>
          <p class="section-label">캘린더</p>
          <h2>월간 축제 일정</h2>
        </div>
        <div class="inline-actions">
          <button
            class="btn btn--secondary btn--small"
            type="button"
            @click="changeMonth(-1)"
          >
            이전 달
          </button>
          <button
            class="btn btn--secondary btn--small"
            type="button"
            @click="goToToday"
          >
            오늘
          </button>
          <button
            class="btn btn--secondary btn--small"
            type="button"
            @click="changeMonth(1)"
          >
            다음 달
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <strong>축제 캘린더를 준비하는 중입니다.</strong>
        <p>잠시만 기다려 주세요.</p>
      </div>
      <div v-else-if="error" class="error-state">
        <strong>축제 정보를 불러오지 못했습니다.</strong>
        <p>{{ error }}</p>
      </div>
      <div v-else>
        <div v-if="filteredFestivals.length > 0 && !hasDatedFestivals" class="empty-state">
          <strong>축제 목록은 준비되었지만 일정 원본은 제공되지 않았습니다.</strong>
          <p>현재 데이터에는 시작일과 종료일이 없어 목록 보기로 자동 전환했습니다.</p>
        </div>
        <FestivalCalendar
          :events="visibleEvents"
          :loading="loading"
          :error="error"
          :initial-date="currentMonth.toISOString().slice(0, 10)"
          @event-click="
            (event) => openFestival(event.extendedProps.originalData)
          "
          @date-click="() => {}"
        />
      </div>
    </section>

    <section v-if="viewMode !== 'calendar'" class="section-card section-block festival-list-section">
      <div class="section-heading">
        <div>
          <p class="section-label">축제 목록</p>
          <h2>선택한 조건의 축제</h2>
        </div>
      </div>

      <div v-if="filteredFestivals.length === 0" class="empty-state">
        <strong>조건에 맞는 축제가 없습니다.</strong>
        <p>다른 검색어나 필터로 다시 확인해 주세요.</p>
      </div>
      <div v-else class="card-list card-list--stacked">
        <article
          v-for="festival in featuredFestivals"
          :key="festival.id || festival.title"
          class="location-card festival-item"
          @click="openFestival(festival)"
        >
          <div class="festival-item__head">
            <div>
              <span class="badge badge--yellow">{{
                festival.category || "축제"
              }}</span>
              <h3>
                {{
                  festival.title ||
                  festival.name ||
                  festival.festivalName ||
                  "축제"
                }}
              </h3>
            </div>
            <span class="badge badge--orange">{{
              getFestivalStatus(festival) === "upcoming"
                ? "예정"
                : getFestivalStatus(festival) === "ongoing"
                  ? "진행 중"
                  : getFestivalStatus(festival) === "unknown"
                    ? "일정 미정"
                  : "종료"
            }}</span>
          </div>
          <p>
            {{
              festival.description ||
              festival.summary ||
              festival.content ||
              "설명이 제공되지 않았습니다."
            }}
          </p>
          <div class="meta-row">
            <span>{{ formatPeriod(festival) }}</span>
            <strong>{{
              festival.place ||
              festival.venue ||
              festival.location ||
              "장소 미정"
            }}</strong>
          </div>
        </article>
      </div>
    </section>

    <FestivalDetailModal
      :festival="selectedFestival"
      :is-open="Boolean(selectedFestival)"
      @close="selectedFestival = null"
    />
  </div>
</template>
