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
    emit("month-change", info.view.calendar.getDate());
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
    if (!date) return;

    const calendarApi = calendarRef.value?.getApi();
    if (!calendarApi) return;

    const targetDate = new Date(`${date}T00:00:00`);
    const displayedDate = calendarApi.getDate();
    const isSameMonth =
      targetDate.getFullYear() === displayedDate.getFullYear() &&
      targetDate.getMonth() === displayedDate.getMonth();

    if (!isSameMonth) {
      calendarApi.gotoDate(targetDate);
    }
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
    <div v-else class="festival-calendar-wrapper">
      <div v-if="events.length === 0" class="festival-calendar-empty-note">
        현재 데이터에는 축제 기간 정보가 없어 일정 바를 표시할 수 없습니다.
      </div>
      <FullCalendar ref="calendarRef" :options="calendarOptions" />
    </div>
  </div>
</template>
