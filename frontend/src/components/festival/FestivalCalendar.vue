<script setup>
import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import listPlugin from "@fullcalendar/list";
import { computed } from "vue";

const props = defineProps({
  events: Array,
  loading: Boolean,
  error: String,
  initialDate: String,
});

const emit = defineEmits(["date-click", "event-click"]);

const calendarOptions = computed(() => ({
  plugins: [dayGridPlugin, interactionPlugin, listPlugin],
  initialView: "dayGridMonth",
  initialDate: props.initialDate,
  headerToolbar: {
    left: "prev today next",
    center: "title",
    right: "dayGridMonth listMonth",
  },
  locale: "ko",
  height: "auto",
  events: props.events,
  eventDisplay: "block",
  dayMaxEvents: 3,
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
  eventContent(arg) {
    const title = arg.event.title || "축제";
    return { html: `<span class="fc-event-title">${title}</span>` };
  },
}));
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
        현재 표시할 축제 일정이 없습니다. 백엔드에서 축제 데이터가 준비되면 바로
        반영됩니다.
      </p>
    </div>
    <div v-else class="festival-calendar-wrapper">
      <FullCalendar :options="calendarOptions" />
    </div>
  </div>
</template>
