<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import brandMark from "../assets/mascot.png";
import { fetchLocations } from "../api/locations";
import { fetchFestivals } from "../api/festivals";
import { parseFestivalDateRange } from "../utils/festivalDate";
import SeoulLocationMap from "../components/common/SeoulLocationMap.vue";

const router = useRouter();
const locations = ref([]);
const loading = ref(true);
const error = ref("");
const activeGuide = ref("");
const selectedMapLocation = ref(null);
const selectedFeaturedLocation = ref(null);
const festivalItems = ref([]);
const festivalLoading = ref(false);
const festivalError = ref("");
const locationTrackRef = ref(null);
const canScrollLocationPrev = ref(false);
const canScrollLocationNext = ref(false);
const isDraggingLocations = ref(false);
const activeLocationCategory = ref("전체");
const locationCategoryCache = new Map();
let locationDragStartX = 0;
let locationDragStartScrollLeft = 0;

const recommendedLocations = computed(() => locations.value);
const locationCategories = [
  { label: "전체", icon: "◎" },
  { label: "관광지", icon: "⌖" },
  { label: "문화시설", icon: "♬" },
  { label: "쇼핑", icon: "♧" },
  { label: "음식점", icon: "♨" },
];
const visibleLocations = computed(() => recommendedLocations.value);

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

function updateLocationScrollState() {
  const track = locationTrackRef.value;
  if (!track) return;

  const maxScrollLeft = Math.max(0, track.scrollWidth - track.clientWidth);
  canScrollLocationPrev.value = track.scrollLeft > 2;
  canScrollLocationNext.value = track.scrollLeft < maxScrollLeft - 2;
}

function scrollLocationTrack(direction) {
  const track = locationTrackRef.value;
  if (!track) return;

  const firstCard = track.firstElementChild;
  const gap = Number.parseFloat(getComputedStyle(track).columnGap) || 0;
  const distance = firstCard ? firstCard.getBoundingClientRect().width + gap : track.clientWidth;
  track.scrollBy({ left: direction * distance, behavior: "smooth" });
}

function startLocationDrag(event) {
  if (event.pointerType === "mouse" && event.button !== 0) return;

  const track = locationTrackRef.value;
  if (!track) return;

  isDraggingLocations.value = true;
  locationDragStartX = event.clientX;
  locationDragStartScrollLeft = track.scrollLeft;
  track.setPointerCapture(event.pointerId);
}

function moveLocationDrag(event) {
  if (!isDraggingLocations.value) return;

  const track = locationTrackRef.value;
  if (!track) return;

  track.scrollLeft = locationDragStartScrollLeft - (event.clientX - locationDragStartX);
  event.preventDefault();
}

function endLocationDrag(event) {
  if (!isDraggingLocations.value) return;

  const track = locationTrackRef.value;
  isDraggingLocations.value = false;
  if (track?.hasPointerCapture(event.pointerId)) {
    track.releasePointerCapture(event.pointerId);
  }
  updateLocationScrollState();
}

function selectMapLocation(location) {
  selectedMapLocation.value = location;
}

function formatLocationSummary(location) {
  const district = location.district && location.district !== "미상" ? location.district : "서울";
  const category = location.category || "명소";
  return `서울 ${district}에서 만나는 ${category}. 잠시 머물며 새로운 서울의 장면을 발견해 보세요.`;
}

async function selectLocationCategory(category) {
  activeLocationCategory.value = category;

  if (locationCategoryCache.has(category)) {
    locations.value = locationCategoryCache.get(category);
  } else {
    loading.value = true;
    error.value = "";
    try {
      const data = await fetchLocations({
        category: category === "전체" ? undefined : category,
        limit: 12,
      });
      const items = Array.isArray(data) ? data : data?.items || [];
      locationCategoryCache.set(category, items);
      locations.value = items;
    } catch (err) {
      error.value = err.message || `${category} 장소를 불러오지 못했습니다.`;
      locations.value = [];
    } finally {
      loading.value = false;
    }
  }

  selectedFeaturedLocation.value = locations.value[0] || null;

  await nextTick();
  if (locationTrackRef.value) {
    locationTrackRef.value.scrollLeft = 0;
  }
  updateLocationScrollState();
}

function handleLocationImageError(event) {
  event.currentTarget.style.display = "none";
  event.currentTarget.parentElement?.classList.add("location-card__visual--fallback");
}

function selectFeaturedLocation(location) {
  selectedFeaturedLocation.value = location;
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
    const categories = locationCategories
      .map((category) => category.label)
      .filter((category) => category !== "전체");
    const responses = await Promise.all(
      categories.map((category) => fetchLocations({ category, limit: 10 })),
    );
    const categoryLists = responses.map((data, index) => {
      const items = Array.isArray(data) ? data : data?.items || [];
      locationCategoryCache.set(categories[index], items);
      return items;
    });

    const mixedItems = [];
    const seenIds = new Set();
    const maxLength = Math.max(0, ...categoryLists.map((items) => items.length));
    for (let itemIndex = 0; itemIndex < maxLength; itemIndex += 1) {
      categoryLists.forEach((items) => {
        const item = items[itemIndex];
        const itemKey = item?.id ?? item?.name;
        if (item && !seenIds.has(itemKey)) {
          seenIds.add(itemKey);
          mixedItems.push(item);
        }
      });
    }

    locationCategoryCache.set("전체", mixedItems);
    activeLocationCategory.value = "전체";
    locations.value = mixedItems;
    selectedFeaturedLocation.value = mixedItems[0] || null;
    await nextTick();
    updateLocationScrollState();
  } catch (err) {
    error.value = err.message || "서울 정보를 불러오지 못했습니다.";
    locations.value = [];
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadLocations();
  window.addEventListener("resize", updateLocationScrollState);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", updateLocationScrollState);
});

watch(visibleLocations, () => {
  if (!selectedMapLocation.value && recommendedLocations.value.length > 0) {
    selectedMapLocation.value = recommendedLocations.value[0];
  }
});
</script>

<template>
  <div class="page-shell home-page">
    <section class="hero-section section-card home-hero">
      <div class="hero-copy">
        <span class="home-eyebrow">SEOUL, CONNECTED</span>
        <h1>서울과<br /><em>다정하게 잇다</em></h1>
        <p>
          익숙한 도시에서 새로운 장면을 발견하는 일. 서울의 장소와 축제,
          사람들의 이야기를 한곳에서 천천히 만나보세요.
        </p>
        <div class="hero-actions">
          <button
            class="btn btn--primary"
            type="button"
            @click="router.push('/festivals')"
          >
            서울 여행 시작하기
          </button>
          <button
            class="btn btn--secondary"
            type="button"
            @click="router.push('/posts')"
          >
            사람들의 이야기
          </button>
        </div>
      </div>

      <div class="hero-visual" aria-hidden="true"></div>
    </section>

    <section class="section-card section-block home-curated">
      <div class="section-heading">
        <div>
          <p class="section-label">CURATED PLACES</p>
          <h2>서울잇다가 고른 장소</h2>
          <p class="page-subtitle">오늘의 기분과 잘 어울리는 서울을 만나보세요.</p>
        </div>
        <div class="inline-actions location-slider-actions">
          <button
            class="location-slider-arrow"
            type="button"
            :disabled="!canScrollLocationPrev"
            aria-label="이전 장소"
            @click="scrollLocationTrack(-1)"
          >
            ‹
          </button>
          <button
            class="location-slider-arrow"
            type="button"
            :disabled="!canScrollLocationNext"
            aria-label="다음 장소"
            @click="scrollLocationTrack(1)"
          >
            ›
          </button>
        </div>
      </div>

      <div class="location-category-tabs" role="tablist" aria-label="장소 카테고리">
        <button
          v-for="category in locationCategories"
          :key="category.label"
          class="location-category-tab"
          :class="{ 'location-category-tab--active': activeLocationCategory === category.label }"
          type="button"
          role="tab"
          :aria-selected="activeLocationCategory === category.label"
          @click="selectLocationCategory(category.label)"
        >
          <span>{{ category.icon }}</span>{{ category.label }}
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
      <div v-else-if="visibleLocations.length === 0" class="empty-state">
        <strong>표시할 장소가 아직 없습니다.</strong>
        <p>지금은 추천 장소를 준비 중입니다. 잠시 후 다시 확인해 주세요.</p>
      </div>
      <div
        v-else
        ref="locationTrackRef"
        class="home-location-track"
        :class="{ 'home-location-track--dragging': isDraggingLocations }"
        @scroll="updateLocationScrollState"
        @pointerdown="startLocationDrag"
        @pointermove="moveLocationDrag"
        @pointerup="endLocationDrag"
        @pointercancel="endLocationDrag"
      >
        <article
          v-for="location in visibleLocations"
          :key="location.id || location.name"
          class="location-card"
          :class="{ 'location-card--selected': selectedFeaturedLocation?.id === location.id }"
          role="button"
          tabindex="0"
          @click="selectFeaturedLocation(location)"
          @keydown.enter="selectFeaturedLocation(location)"
        >
          <div class="location-card__visual">
            <img
              v-if="location.image_url || location.thumbnail_url"
              :src="location.image_url || location.thumbnail_url"
              :alt="`${location.name} 대표 이미지`"
              loading="lazy"
              @error="handleLocationImageError"
            />
            <span>SEOUL ITDA</span>
          </div>
          <div class="location-card__header">
            <span :class="['badge', getCategoryTone(location.category)]">
              {{ getCategoryLabel(location.category) }}
            </span>
            <h3>{{ location.name || location.title || '이름 미정' }}</h3>
          </div>
          <p>{{ formatLocationSummary(location) }}</p>
          <span class="location-card__more">자세히 보기 →</span>
        </article>
      </div>

      <section v-if="selectedFeaturedLocation" class="featured-place-detail">
        <div class="featured-place-card">
          <div class="featured-place-card__photo">
            <img
              v-if="selectedFeaturedLocation.image_url || selectedFeaturedLocation.thumbnail_url"
              :src="selectedFeaturedLocation.image_url || selectedFeaturedLocation.thumbnail_url"
              :alt="`${selectedFeaturedLocation.name} 전경`"
              @error="handleLocationImageError"
            />
          </div>
          <div class="featured-place-card__copy">
            <span class="badge badge--mint">{{ selectedFeaturedLocation.category }}</span>
            <h3>{{ selectedFeaturedLocation.name }}</h3>
            <p>{{ formatLocationSummary(selectedFeaturedLocation) }}</p>
            <dl class="featured-place-info">
              <div>
                <dt>주소</dt>
                <dd>{{ formatLocationAddress(selectedFeaturedLocation) }}</dd>
              </div>
              <div>
                <dt>전화</dt>
                <dd>{{ selectedFeaturedLocation.telephone || "전화번호 정보 없음" }}</dd>
              </div>
            </dl>
            <a
              class="btn btn--primary featured-place-card__map-link"
              :href="`https://map.naver.com/p/search/${encodeURIComponent([selectedFeaturedLocation.name, selectedFeaturedLocation.address].filter(Boolean).join(' '))}`"
              target="_blank"
              rel="noopener noreferrer"
            >지도에서 크게 보기</a>
          </div>
        </div>
        <SeoulLocationMap
          :locations="visibleLocations"
          :selected-location="selectedFeaturedLocation"
          @select="selectFeaturedLocation"
        />
      </section>
    </section>

    <section class="home-about">
      <div>
        <p class="section-label">ABOUT SEOUL ITDA</p>
        <h2>도시와 사람을<br />이어주는 여행</h2>
        <p>서울잇다는 여행자에게는 좋은 장소를, 서울을 살아가는 사람에게는 새로운 일상을 건넵니다. 무엇을 해야 할지 고민되는 날, 가볍게 펼쳐보는 서울 안내서가 되어드릴게요.</p>
        <button class="btn btn--paper" type="button" @click="router.push('/posts')">서울잇다 이야기</button>
      </div>
      <div class="home-about__doodle" aria-hidden="true">
        <span>⌁</span><strong>서울의 하루</strong><small>걷고 · 보고 · 나누기</small>
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
