<script setup>
import { computed, onBeforeUnmount, watch } from "vue";

const props = defineProps({
  festival: Object,
  isOpen: Boolean,
});

const emit = defineEmits(["close"]);

const hasImage = computed(() => Boolean(props.festival?.imageUrl));

function handleKeydown(event) {
  if (event.key === "Escape") {
    emit("close");
  }
}

function syncBodyScrollLock(isOpen) {
  document.body.style.overflow = isOpen ? "hidden" : "";
}

watch(
  () => props.isOpen,
  (isOpen) => {
    syncBodyScrollLock(Boolean(isOpen));
  },
  { immediate: true },
);

document.addEventListener("keydown", handleKeydown);

onBeforeUnmount(() => {
  document.removeEventListener("keydown", handleKeydown);
  syncBodyScrollLock(false);
});
</script>

<template>
  <div
    v-if="isOpen && festival"
    class="modal-backdrop"
    role="dialog"
    aria-modal="true"
    @click="emit('close')"
  >
    <div class="modal-card section-card" @click.stop>
      <div class="modal-card__header">
        <div>
          <p class="section-label">축제 상세</p>
          <h3>{{ festival.title }}</h3>
        </div>
        <button class="icon-button" type="button" @click="emit('close')">
          닫기
        </button>
      </div>

      <div class="modal-card__body">
        <div v-if="hasImage" class="modal-card__image">
          <img
            :src="festival.imageUrl"
            :alt="festival.title"
            @error="$event.target.style.display = 'none'"
          />
        </div>
        <div v-else class="empty-state">
          <strong>이미지 정보가 없습니다.</strong>
          <p>공식 자료에서 이미지가 제공되면 이곳에 표시됩니다.</p>
        </div>

        <div class="detail-list">
          <div v-if="festival.period" class="detail-row">
            <span>기간</span><strong>{{ festival.period }}</strong>
          </div>
          <div v-if="festival.place" class="detail-row">
            <span>장소</span><strong>{{ festival.place }}</strong>
          </div>
          <div v-if="festival.address" class="detail-row">
            <span>주소</span><strong>{{ festival.address }}</strong>
          </div>
          <div v-if="festival.description" class="detail-row">
            <span>설명</span><strong>{{ festival.description }}</strong>
          </div>
          <div v-if="festival.phone" class="detail-row">
            <span>문의</span><strong>{{ festival.phone }}</strong>
          </div>
          <div v-if="festival.category" class="detail-row">
            <span>카테고리</span><strong>{{ festival.category }}</strong>
          </div>
        </div>
      </div>

      <div class="modal-card__footer">
        <a
          v-if="festival.homepageUrl"
          :href="festival.homepageUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="btn btn--primary"
          >공식 홈페이지</a
        >
        <button class="btn btn--secondary" type="button" @click="emit('close')">
          닫기
        </button>
      </div>
    </div>
  </div>
</template>
