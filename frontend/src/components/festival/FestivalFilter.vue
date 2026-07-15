<script setup>
const props = defineProps({
  filters: Object,
});

const emit = defineEmits(["update:filters", "reset", "apply"]);

function updateFilter(key, value) {
  emit("update:filters", { ...props.filters, [key]: value });
}
</script>

<template>
  <section class="festival-filter section-card">
    <div class="festival-filter__header">
      <div>
        <p class="section-label">FIND YOUR FESTIVAL</p>
        <h3>원하는 축제를 찾아보세요</h3>
      </div>
      <button
        class="btn btn--ghost btn--small"
        type="button"
        @click="emit('reset')"
      >
        초기화
      </button>
    </div>

    <div class="festival-filter__controls">
      <label class="field">
        <span>축제명</span>
        <input
          class="input"
          :value="filters.keyword"
          placeholder="축제명을 입력하세요"
          @input="updateFilter('keyword', $event.target.value)"
        />
      </label>

      <label class="field">
        <span>진행 상태</span>
        <select
          class="input"
          :value="filters.status"
          @change="updateFilter('status', $event.target.value)"
        >
          <option value="">전체</option>
          <option value="upcoming">예정</option>
          <option value="ongoing">진행 중</option>
          <option value="ended">종료</option>
        </select>
      </label>

      <label class="field">
        <span>시작일</span>
        <input
          class="input"
          type="date"
          :value="filters.startDate"
          @input="updateFilter('startDate', $event.target.value)"
        />
      </label>

      <label class="field">
        <span>종료일</span>
        <input
          class="input"
          type="date"
          :value="filters.endDate"
          @input="updateFilter('endDate', $event.target.value)"
        />
      </label>
    </div>

    <div class="festival-filter__footer">
      <p class="helper-text">이름과 기간, 진행 상태를 조합해 일정을 찾아보세요.</p>
      <div class="inline-actions">
        <button
          class="btn btn--primary btn--small"
          type="button"
          @click="emit('apply')"
        >
          검색 적용
        </button>
      </div>
    </div>
  </section>
</template>
