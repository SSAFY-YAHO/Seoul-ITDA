<script setup>
import { computed } from "vue";

const props = defineProps({
  locations: { type: Array, default: () => [] },
  selectedLocation: { type: Object, default: null },
});

const emit = defineEmits(["select"]);

const SEOUL_BOUNDS = {
  minLongitude: 126.76,
  maxLongitude: 127.19,
  minLatitude: 37.43,
  maxLatitude: 37.70,
};

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function projectLocation(location) {
  const longitude = Number(location.longitude);
  const latitude = Number(location.latitude);
  if (!Number.isFinite(longitude) || !Number.isFinite(latitude)) return null;

  const xRatio = (longitude - SEOUL_BOUNDS.minLongitude)
    / (SEOUL_BOUNDS.maxLongitude - SEOUL_BOUNDS.minLongitude);
  const yRatio = (SEOUL_BOUNDS.maxLatitude - latitude)
    / (SEOUL_BOUNDS.maxLatitude - SEOUL_BOUNDS.minLatitude);
  return {
    ...location,
    x: 82 + clamp(xRatio, 0, 1) * 452,
    y: 46 + clamp(yRatio, 0, 1) * 402,
  };
}

const mapLocations = computed(() => props.locations.map(projectLocation).filter(Boolean));
</script>

<template>
  <div class="seoul-location-map">
    <div class="seoul-location-map__title">
      <span>SEOUL MAP</span>
      <strong>지도에서 장소를 골라보세요</strong>
    </div>
    <svg viewBox="0 0 620 500" role="img" aria-label="서울 장소 위치 지도">
      <defs>
        <filter id="mapShadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="#315c4d" flood-opacity=".16" />
        </filter>
      </defs>
      <path
        class="seoul-map-shape"
        filter="url(#mapShadow)"
        d="M294 24 C345 20 377 49 410 73 C447 100 506 101 534 139 C562 178 535 220 548 257 C560 293 535 320 511 347 C487 374 492 421 452 441 C411 463 374 441 337 459 C302 476 258 458 237 426 C216 394 176 397 149 369 C119 339 130 300 101 273 C72 246 67 205 91 175 C115 145 153 132 174 101 C199 64 244 36 294 24 Z"
      />
      <path class="seoul-map-river" d="M82 275 C152 239 198 290 263 257 C330 224 376 272 442 246 C488 228 522 233 548 244" />
      <g class="seoul-map-districts" aria-hidden="true">
        <path d="M174 101 C222 128 249 113 278 64" />
        <path d="M278 64 C311 112 351 114 410 73" />
        <path d="M149 369 C190 338 215 326 237 276" />
        <path d="M237 276 C265 322 312 329 337 459" />
        <path d="M337 459 C363 369 408 337 511 347" />
        <path d="M442 246 C432 184 472 155 534 139" />
        <path d="M263 257 C271 194 234 162 174 101" />
        <path d="M263 257 C337 214 347 153 410 73" />
      </g>
      <g class="seoul-map-labels" aria-hidden="true">
        <text x="265" y="92">은평·서대문</text>
        <text x="395" y="130">강북·노원</text>
        <text x="176" y="216">마포</text>
        <text x="290" y="215">종로·중구</text>
        <text x="420" y="216">성동·광진</text>
        <text x="183" y="350">강서·구로</text>
        <text x="311" y="389">관악·동작</text>
        <text x="425" y="354">강남·송파</text>
      </g>
      <g v-for="location in mapLocations" :key="location.id || location.name">
        <g
          class="seoul-map-marker"
          :class="{ 'seoul-map-marker--active': selectedLocation?.id === location.id }"
          :transform="`translate(${location.x} ${location.y})`"
          role="button"
          tabindex="0"
          :aria-label="`${location.name} 선택`"
          @click="emit('select', location)"
          @keydown.enter="emit('select', location)"
        >
          <circle r="12" />
          <circle r="4" />
          <text v-if="selectedLocation?.id === location.id" x="17" y="5">{{ location.name }}</text>
        </g>
      </g>
    </svg>
    <p v-if="mapLocations.length === 0" class="seoul-location-map__empty">좌표가 등록된 장소가 없습니다.</p>
  </div>
</template>
