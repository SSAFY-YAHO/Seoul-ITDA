<script setup>
import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import { computed, ref, watch } from "vue";

const props = defineProps({
  events: Array,
  loading: Boolean,
  error: String,
  initialDate: String,
});

const emit = defineEmits(["date-click", "event-click", "month-change"]);
const calendarRef = ref(null);

function getEventTone(event) {
  const source = `${event.id}-${event.title}`;
  const toneIndex = [...source].reduce((sum, character) => sum + character.charCodeAt(0), 0) % 4;
  return `festival-event--tone-${toneIndex + 1}`;
}

const calendarOptions = computed(() => ({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: "dayGridMonth",
  initialDate: props.initialDate,
  headerToolbar: {
    left: "",
    center: "title",
    right: "",
  },
  locale: "ko",
  titleFormat: { year: "numeric", month: "long" },
  dayHeaderFormat: { weekday: "long" },
  height: "auto",
  fixedWeekCount: false,
  showNonCurrentDates: true,
  events: props.events,
  eventDisplay: "block",
  displayEventTime: false,
  dayMaxEvents: 4,
  moreLinkText: "+ 더 보기",
  eventTimeFormat: {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  },
  eventClick(info) {
    emit("event-click", info.event);
  },
  dateClick(info) {
    emit("date-click", info);
  },
  datesSet(info) {
    emit("month-change", info.view.currentStart);
  },
  eventClassNames(info) {
    return [getEventTone(info.event)];
  },
  eventContent(arg) {
    const title = arg.event.title || "축제";
    return { html: `<span class="fc-event-title">${title}</span>` };
  },
}));

watch(
  () => props.initialDate,
  (date) => {
    if (date) calendarRef.value?.getApi().gotoDate(date);
  },
);
</script>

<template>
  <div class="festival-calendar-card section-card">
    <div v-if="loading" class="loading-state">
      <strong>축제 정보를 불러오는 중입니다.</strong>
      <p>캘린더를 준비하고 있습니다.</p>
    </div>
    <div v-else-if="error" class="error-state">
      <strong>축제 정보를 불러오지 못했습니다.</strong>
      <p>{{ error }}</p>
    </div>
    <div v-else-if="events.length === 0" class="empty-state">
      <strong>축제 데이터를 준비 중입니다.</strong>
      <p>
        현재 표시할 축제 일정이 없습니다. 다른 조건으로 검색하거나 목록 보기로
        확인해 주세요.
      </p>
    </div>
    <div v-else class="festival-calendar-wrapper">
      <FullCalendar ref="calendarRef" :options="calendarOptions" />
    </div>
  </div>
</template>
