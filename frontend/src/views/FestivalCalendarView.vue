<script setup>
import { computed, onMounted, ref } from "vue";
import FestivalCalendar from "../components/festival/FestivalCalendar.vue";
import FestivalDetailModal from "../components/festival/FestivalDetailModal.vue";
import FestivalFilter from "../components/festival/FestivalFilter.vue";
import { fetchFestivals } from "../api/festivals";
import {
  parseFestivalDateRange,
  toCalendarEvent,
} from "../utils/festivalDate.js";
import brandMark from "../assets/mascot.png";

const loading = ref(true);
const error = ref("");
const festivalItems = ref([]);
const festivalTotal = ref(0);
const selectedFestival = ref(null);
const festivalCalendarRef = ref(null);
const filters = ref({
  keyword: "",
  status: "",
  startDate: "",
  endDate: "",
});
const currentMonth = ref(new Date());
const initialCalendarDate = computed(() =>
  `${currentMonth.value.getFullYear()}-${String(currentMonth.value.getMonth() + 1).padStart(2, "0")}-${String(currentMonth.value.getDate()).padStart(2, "0")}`,
);

function getFestivalStatus(item) {
  const parsed = parseFestivalDateRange(item);
  if (!parsed) return "unknown";
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const end = new Date(parsed.end);
  end.setDate(end.getDate() - 1);
  end.setHours(23, 59, 59, 999);
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
  festivalCalendarRef.value?.goToToday();
}

function changeMonth(step) {
  if (step < 0) {
    festivalCalendarRef.value?.goToPreviousMonth();
  } else if (step > 0) {
    festivalCalendarRef.value?.goToNextMonth();
  }
}

function syncCurrentMonth(date) {
  const isSameMonth =
    currentMonth.value.getFullYear() === date.getFullYear() &&
    currentMonth.value.getMonth() === date.getMonth();

  if (!isSameMonth) {
    currentMonth.value = new Date(date.getFullYear(), date.getMonth(), 1);
  }
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
  <div class="page-shell festival-page">
    <section class="section-card hero-section festival-hero">
      <div class="hero-copy">
        <span class="home-eyebrow">SEOUL FESTIVAL CALENDAR</span>
        <h1>계절마다 피어나는<br /><em>서울의 축제</em></h1>
        <p>
          오늘의 서울에는 어떤 즐거움이 기다리고 있을까요? 날짜를 넘기며
          공연과 전시, 다채로운 축제의 순간을 발견해 보세요.
        </p>
      </div>
      <div class="hero-visual festival-hero-art" aria-label="서울 축제 달력 일러스트">
        <div class="festival-hero-art__sun"></div>
        <div class="festival-hero-art__calendar">
          <span>{{ currentMonth.getFullYear() }}</span>
          <strong>{{ currentMonth.getMonth() + 1 }}</strong>
          <small>SEOUL FESTIVAL</small>
        </div>
        <div class="festival-hero-art__mascot">
          <img :src="brandMark" alt="서울잇다 해치 아이콘" />
        </div>
        <i class="festival-hero-art__flower festival-hero-art__flower--one">✦</i>
        <i class="festival-hero-art__flower festival-hero-art__flower--two">✿</i>
      </div>
    </section>

    <FestivalFilter
      :filters="filters"
      @update:filters="filters = $event"
      @apply="loadFestivals"
      @reset="resetFilters"
    />

    <section class="section-card section-block festival-calendar-section">
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
          ref="festivalCalendarRef"
          :events="visibleEvents"
          :loading="loading"
          :error="error"
          :initial-date="initialCalendarDate"
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
