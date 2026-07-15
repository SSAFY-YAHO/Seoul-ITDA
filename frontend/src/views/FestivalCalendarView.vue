<script setup>
import { computed, onMounted, ref } from "vue";
import FestivalDetailModal from "../components/festival/FestivalDetailModal.vue";
import FestivalFilter from "../components/festival/FestivalFilter.vue";
import { fetchFestivals } from "../api/festivals";
import { fetchLocations } from "../api/locations";
import { parseFestivalDateRange } from "../utils/festivalDate.js";
import brandMark from "../assets/mascot.png";

const loading = ref(true);
const error = ref("");
const festivalItems = ref([]);
const locationItems = ref([]);
const locationsLoading = ref(false);
const selectedFestival = ref(null);
const favoriteIds = ref([]);
const hoveredFestivalId = ref("");
const filters = ref({
  keyword: "",
  status: "",
  startDate: "",
  endDate: "",
});
const currentMonth = ref(new Date());

const currentMonthLabel = computed(() =>
  currentMonth.value.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
  }),
);

const favoriteFestivals = computed(() =>
  festivalItems.value.filter((festival) => favoriteIds.value.includes(String(festival.id))),
);

function coordinatesOf(item) {
  const longitude = Number(item.longitude);
  const latitude = Number(item.latitude);
  return Number.isFinite(longitude) && Number.isFinite(latitude)
    ? { longitude, latitude }
    : null;
}

function distanceInKilometers(from, to) {
  const radians = (degree) => degree * (Math.PI / 180);
  const earthRadius = 6371;
  const latitudeGap = radians(to.latitude - from.latitude);
  const longitudeGap = radians(to.longitude - from.longitude);
  const value = Math.sin(latitudeGap / 2) ** 2
    + Math.cos(radians(from.latitude)) * Math.cos(radians(to.latitude))
    * Math.sin(longitudeGap / 2) ** 2;
  return earthRadius * 2 * Math.atan2(Math.sqrt(value), Math.sqrt(1 - value));
}

const nearbyLocations = computed(() => {
  const festivals = favoriteFestivals.value
    .map((festival) => ({ festival, coordinates: coordinatesOf(festival) }))
    .filter((item) => item.coordinates);

  if (!festivals.length) return [];

  return locationItems.value
    .map((location) => {
      const coordinates = coordinatesOf(location);
      if (!coordinates) return null;
      const nearest = festivals
        .map((item) => ({
          festival: item.festival,
          distance: distanceInKilometers(item.coordinates, coordinates),
        }))
        .sort((a, b) => a.distance - b.distance)[0];
      return { location, ...nearest };
    })
    .filter(Boolean)
    .sort((a, b) => a.distance - b.distance)
    .slice(0, 6);
});

function locationImage(location) {
  return location.image_url || location.thumbnail_url || "";
}

function locationMapUrl(location) {
  const coordinates = coordinatesOf(location);
  const query = coordinates
    ? `${coordinates.latitude},${coordinates.longitude}`
    : [location.name, location.address].filter(Boolean).join(" ");
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`;
}

function dateOnly(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function getFestivalTone(festival) {
  const source = String(festival.id || festival.title || "festival");
  const tone = [...source].reduce((sum, character) => sum + character.charCodeAt(0), 0) % 4;
  return `festival-tone-${tone + 1}`;
}

const festivalColorMap = computed(() => {
  const ids = [...new Set(festivalItems.value.map((festival) => String(festival.id)))]
    .sort((a, b) => a.localeCompare(b, "ko", { numeric: true }));
  const colors = new Map();
  ids.forEach((id, index) => {
    const hue = Math.round((index * 137.508 + 88) % 360);
    colors.set(id, {
      backgroundColor: `hsl(${hue} 55% 79%)`,
      color: "#1f2521",
    });
  });
  return colors;
});

const practicalFestivalGroups = computed(() => {
  const monthStart = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth(), 1);
  const monthEnd = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() + 1, 1);
  const normalized = festivalItems.value
    .map((festival) => ({ festival, range: parseFestivalDateRange(festival) }))
    .filter((item) => item.range);

  const thisMonth = normalized
    .filter(({ range }) => range.start < monthEnd && range.end > monthStart)
    .sort((a, b) => a.range.start - b.range.start)
    .map(({ festival }) => festival);

  return [
    { key: "month", eyebrow: "MONTHLY PICKS", title: `${currentMonthLabel.value} 행사`, items: thisMonth },
  ];
});

const miniCalendarDays = computed(() => {
  const year = currentMonth.value.getFullYear();
  const month = currentMonth.value.getMonth();
  const firstDay = new Date(year, month, 1);
  const gridStart = new Date(year, month, 1 - firstDay.getDay());
  const today = dateOnly(new Date());
  const laneEnds = [new Date(0), new Date(0)];
  const festivalLanes = new Map();
  festivalItems.value
    .map((festival) => ({ festival, range: parseFestivalDateRange(festival) }))
    .filter((item) => item.range)
    .sort((a, b) => a.range.start - b.range.start || b.range.end - a.range.end)
    .forEach(({ festival, range }) => {
      const lane = laneEnds.findIndex((laneEnd) => range.start >= laneEnd);
      if (lane >= 0) {
        festivalLanes.set(String(festival.id), lane);
        laneEnds[lane] = range.end;
      }
    });

  return Array.from({ length: 42 }, (_, index) => {
    const date = new Date(gridStart);
    date.setDate(gridStart.getDate() + index);
    const festivals = festivalItems.value.map((festival) => {
      const range = parseFestivalDateRange(festival);
      if (!range || date < dateOnly(range.start) || date >= dateOnly(range.end)) return null;
      const lane = festivalLanes.get(String(festival.id));
      if (lane === undefined) return null;
      const nextDate = new Date(date);
      nextDate.setDate(nextDate.getDate() + 1);
      return {
        festival,
        tone: getFestivalTone(festival),
        color: festivalColorMap.value.get(String(festival.id)),
        isFavorite: favoriteIds.value.includes(String(festival.id)),
        lane,
        isStart: date.getTime() === dateOnly(range.start).getTime(),
        isEnd: nextDate.getTime() === dateOnly(range.end).getTime(),
      };
    }).filter(Boolean).sort((a, b) => a.lane - b.lane);
    return {
      key: date.toISOString(),
      date,
      day: date.getDate(),
      isCurrentMonth: date.getMonth() === month,
      isToday: date.getTime() === today.getTime(),
      festivals,
    };
  });
});

function isFavorite(festival) {
  return favoriteIds.value.includes(String(festival.id));
}

function toggleFavorite(festival) {
  const id = String(festival.id);
  favoriteIds.value = isFavorite(festival)
    ? favoriteIds.value.filter((item) => item !== id)
    : [...favoriteIds.value, id];
  localStorage.setItem("seoul-itda-favorite-festivals", JSON.stringify(favoriteIds.value));
}

function restoreFestivalPreferences() {
  try {
    favoriteIds.value = JSON.parse(localStorage.getItem("seoul-itda-favorite-festivals") || "[]");
  } catch (_error) {
    favoriteIds.value = [];
  }
}

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
    longitude: festival.longitude ?? null,
    latitude: festival.latitude ?? null,
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

async function loadLocations() {
  locationsLoading.value = true;
  try {
    const data = await fetchLocations({ limit: 50 });
    locationItems.value = Array.isArray(data) ? data : data?.items || [];
  } catch (_error) {
    locationItems.value = [];
  } finally {
    locationsLoading.value = false;
  }
}

function moveMiniCalendarMonth(step) {
  currentMonth.value = new Date(
    currentMonth.value.getFullYear(),
    currentMonth.value.getMonth() + step,
    1,
  );
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
  restoreFestivalPreferences();
  loadFestivals();
  loadLocations();
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

    <section class="festival-discovery" aria-labelledby="festival-discovery-title">
      <div class="festival-discovery__heading">
        <div>
          <p class="section-label">FESTIVAL NOW</p>
          <h2 id="festival-discovery-title">지금 가기 좋은 축제</h2>
          <p>월간 목록보다 실용적인 기준으로 가까운 일정을 먼저 확인해 보세요.</p>
        </div>
        <div class="festival-favorite-count">♥ 찜한 축제 {{ favoriteIds.length }}</div>
      </div>

      <div class="festival-discovery__body">
        <div class="festival-practical-grid">
          <section v-for="group in practicalFestivalGroups" :key="group.key" class="festival-practical-group">
          <header>
            <span>{{ group.eyebrow }}</span>
            <h3>{{ group.title }}</h3>
          </header>
          <div v-if="group.items.length" class="festival-discovery-list">
            <article v-for="festival in group.items" :key="festival.id" class="festival-discovery-card">
              <button class="festival-discovery-card__main" type="button" @click="openFestival(festival)">
                <span class="festival-discovery-card__image">
                  <img v-if="festival.imageUrl" :src="festival.imageUrl" :alt="festival.title" loading="lazy" />
                </span>
                <span class="festival-discovery-card__copy">
                  <b>{{ festival.title }}</b>
                  <small>{{ formatPeriod(festival) }}</small>
                  <em>{{ festival.region || "서울" }}</em>
                </span>
              </button>
              <div class="festival-discovery-card__actions">
                <button type="button" :class="{ active: isFavorite(festival) }" @click="toggleFavorite(festival)">
                  {{ isFavorite(festival) ? "♥ 찜됨" : "♡ 찜" }}
                </button>
              </div>
            </article>
          </div>
          <div v-else class="festival-practical-empty">해당하는 축제가 아직 없습니다.</div>
          </section>
        </div>

        <aside class="festival-mini-calendar">
          <header>
            <div>
              <span>MONTHLY CALENDAR</span>
              <h3>{{ currentMonthLabel }}</h3>
            </div>
            <div class="festival-mini-calendar__navigation">
              <button type="button" aria-label="이전 달" @click="moveMiniCalendarMonth(-1)">‹</button>
              <button type="button" @click="goToToday">오늘</button>
              <button type="button" aria-label="다음 달" @click="moveMiniCalendarMonth(1)">›</button>
            </div>
          </header>
          <div class="festival-mini-calendar__weekdays" aria-hidden="true">
            <span>일</span><span>월</span><span>화</span><span>수</span><span>목</span><span>금</span><span>토</span>
          </div>
          <div class="festival-mini-calendar__days">
            <div
              v-for="day in miniCalendarDays"
              :key="day.key"
              :class="{
                'is-outside': !day.isCurrentMonth,
                'is-today': day.isToday,
                'has-festival': day.festivals.length > 0,
              }"
            >
              <span class="festival-mini-calendar__day-number">{{ day.day }}</span>
              <span class="festival-mini-calendar__events">
                <i
                  v-for="item in day.festivals.slice(0, 2)"
                  :key="item.festival.id"
                  :class="{
                    'is-start': item.isStart,
                    'is-end': item.isEnd,
                    'is-middle': !item.isStart && !item.isEnd,
                    'is-favorite': item.isFavorite,
                    'is-hovered': hoveredFestivalId === String(item.festival.id),
                    [item.tone]: true,
                  }"
                  :title="item.festival.title"
                  :style="{ gridRow: item.lane + 1, ...item.color }"
                  role="button"
                  tabindex="0"
                  :aria-label="`${item.festival.title} ${item.isFavorite ? '찜 해제' : '찜하기'}`"
                  @mouseenter="hoveredFestivalId = String(item.festival.id)"
                  @mouseleave="hoveredFestivalId = ''"
                  @click.stop="toggleFavorite(item.festival)"
                  @keydown.enter.stop="toggleFavorite(item.festival)"
                >{{ item.isStart ? item.festival.title : "" }}</i>
                <small v-if="day.festivals.length > 2">+{{ day.festivals.length - 2 }}</small>
              </span>
            </div>
          </div>
        </aside>
      </div>
    </section>

    <section class="festival-nearby" aria-labelledby="festival-nearby-title">
      <header class="festival-nearby__heading">
        <div>
          <p class="section-label">NEAR YOUR FESTIVAL</p>
          <h2 id="festival-nearby-title">찜한 축제와 가까운 서울</h2>
          <p>찜한 행사의 위치를 기준으로 함께 둘러보기 좋은 장소를 가까운 순서로 추천해드려요.</p>
        </div>
        <span v-if="nearbyLocations.length">가까운 장소 {{ nearbyLocations.length }}곳</span>
      </header>

      <div v-if="locationsLoading" class="festival-nearby__empty">가까운 장소를 찾고 있어요.</div>
      <div v-else-if="favoriteIds.length === 0" class="festival-nearby__empty">
        <b>먼저 가고 싶은 축제를 찜해보세요.</b>
        <span>추천 카드나 캘린더의 행사 막대를 누르면 주변 장소가 여기에 나타납니다.</span>
      </div>
      <div v-else-if="nearbyLocations.length === 0" class="festival-nearby__empty">
        <b>위치 정보가 있는 주변 장소를 찾지 못했어요.</b>
        <span>다른 축제를 찜하면 새로운 추천을 확인할 수 있습니다.</span>
      </div>
      <div v-else class="festival-nearby__grid">
        <article v-for="item in nearbyLocations" :key="item.location.id" class="festival-nearby-card">
          <a :href="locationMapUrl(item.location)" target="_blank" rel="noopener noreferrer">
            <span class="festival-nearby-card__image">
              <img v-if="locationImage(item.location)" :src="locationImage(item.location)" :alt="item.location.name" loading="lazy" />
              <i v-else>SEOUL</i>
              <em>{{ item.distance < 1 ? `${Math.round(item.distance * 1000)}m` : `${item.distance.toFixed(1)}km` }}</em>
            </span>
            <span class="festival-nearby-card__copy">
              <small>{{ item.location.category || "서울 명소" }}</small>
              <b>{{ item.location.name }}</b>
              <span>{{ item.location.address || item.location.district || "주소 정보 확인 중" }}</span>
              <strong>‘{{ item.festival.title }}’에서 가까워요 <i>↗</i></strong>
            </span>
          </a>
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
