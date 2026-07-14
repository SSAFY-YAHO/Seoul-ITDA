<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import FestivalCalendar from "../components/festival/FestivalCalendar.vue";
import FestivalDetailModal from "../components/festival/FestivalDetailModal.vue";
import FestivalFilter from "../components/festival/FestivalFilter.vue";
import { fetchFestivals } from "../api/festivals";
import {
  parseFestivalDateRange,
  toCalendarEvent,
} from "../utils/festivalDate.js";
import brandMark from "../assets/mascot.png";

const router = useRouter();

const loading = ref(true);
const error = ref("");
const festivalItems = ref([]);
const festivalTotal = ref(0);
const selectedFestival = ref(null);
const filters = ref({
  keyword: "",
  status: "",
  startDate: "",
  endDate: "",
});
const currentMonth = ref(new Date());

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
  return festivalItems.value;
});

const visibleEvents = computed(() =>
  filteredFestivals.value
    .map((festival, index) => toCalendarEvent(festival, index))
    .filter(Boolean),
);

const monthlyFestivals = computed(() => {
  const monthStart = new Date(
    currentMonth.value.getFullYear(),
    currentMonth.value.getMonth(),
    1,
  );
  const nextMonth = new Date(
    currentMonth.value.getFullYear(),
    currentMonth.value.getMonth() + 1,
    1,
  );

  return filteredFestivals.value
    .filter((festival) => {
      const range = parseFestivalDateRange(festival);
      return range && range.start < nextMonth && range.end > monthStart;
    })
    .sort((a, b) => {
    const aDate = parseFestivalDateRange(a)?.start;
    const bDate = parseFestivalDateRange(b)?.start;

    if (aDate && bDate) {
      return aDate - bDate;
    }
    if (aDate) return -1;
    if (bDate) return 1;

    return String(a.title || a.name || "").localeCompare(String(b.title || b.name || ""), "ko");
    });
});

const currentMonthLabel = computed(() =>
  currentMonth.value.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
  }),
);

function formatPeriod(item) {
  const parsed = parseFestivalDateRange(item);
  if (!parsed) return "기간 정보 미정";
  const inclusiveEnd = new Date(parsed.end);
  inclusiveEnd.setDate(inclusiveEnd.getDate() - 1);
  return `${parsed.start.toLocaleDateString("ko-KR", { month: "short", day: "numeric" })} ~ ${inclusiveEnd.toLocaleDateString("ko-KR", { month: "short", day: "numeric" })}`;
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
    const data = await fetchFestivals({
      q: filters.value.keyword,
      status: filters.value.status,
      startDate: filters.value.startDate,
      endDate: filters.value.endDate,
    });
    const items = Array.isArray(data) ? data : data?.items || [];
    festivalItems.value = items;
    festivalTotal.value = Array.isArray(data) ? items.length : data?.total || items.length;
  } catch (err) {
    error.value = err.message || "축제 정보를 불러오지 못했습니다.";
    festivalItems.value = [];
    festivalTotal.value = 0;
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

function syncCurrentMonth(date) {
  currentMonth.value = new Date(date.getFullYear(), date.getMonth(), 1);
}

function resetFilters() {
  filters.value = {
    keyword: "",
    status: "",
    startDate: "",
    endDate: "",
  };
  loadFestivals();
}

onMounted(() => {
  loadFestivals();
});

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
      @update:filters="filters = $event"
      @apply="loadFestivals"
      @reset="resetFilters"
    />

    <section class="section-card section-block">
      <div class="section-heading">
        <div>
          <p class="section-label">캘린더</p>
          <h2>월간 축제 일정</h2>
          <p class="page-subtitle">검색 결과 {{ festivalTotal }}건</p>
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
      <div v-else class="festival-calendar-layout">
        <FestivalCalendar
          :events="visibleEvents"
          :loading="loading"
          :error="error"
          :initial-date="currentMonth.toISOString().slice(0, 10)"
          @event-click="(event) => openFestival(event.extendedProps.originalData)"
          @month-change="syncCurrentMonth"
          @date-click="() => {}"
        />

        <aside class="festival-monthly-panel">
          <div class="festival-monthly-panel__header">
            <p class="section-label">월별 축제</p>
            <h3>{{ currentMonthLabel }}</h3>
            <p class="helper-text">이 달에 진행되는 축제 {{ monthlyFestivals.length }}건</p>
          </div>

          <div v-if="monthlyFestivals.length === 0" class="empty-state">
            <strong>이 달에 진행되는 축제가 없습니다.</strong>
            <p>다른 달로 이동해 일정을 확인해 주세요.</p>
          </div>
          <div v-else class="festival-monthly-list">
            <button
              v-for="festival in monthlyFestivals"
              :key="festival.id || festival.title || festival.name"
              class="festival-monthly-item"
              type="button"
              @click="openFestival(festival)"
            >
              <span class="badge badge--orange">{{
                getFestivalStatus(festival) === "upcoming"
                  ? "예정"
                  : getFestivalStatus(festival) === "ongoing"
                    ? "진행 중"
                    : "종료"
              }}</span>
              <strong>{{ festival.title || festival.name || festival.festivalName || "축제" }}</strong>
              <span>{{ formatPeriod(festival) }}</span>
              <small>{{ festival.place || festival.venue || festival.location || "장소 미정" }}</small>
            </button>
          </div>
        </aside>
      </div>
    </section>

    <FestivalDetailModal
      :festival="selectedFestival"
      :is-open="Boolean(selectedFestival)"
      @close="selectedFestival = null"
    />
  </div>
</template>
