<script setup>
const props = defineProps({
  filters: Object,
  viewMode: String,
});

const emit = defineEmits(["update:filters", "update:viewMode", "reset", "apply"]);

function updateFilter(key, value) {
  emit("update:filters", { ...props.filters, [key]: value });
}
</script>

<template>
  <section class="festival-filter section-card">
    <div class="festival-filter__header">
      <div>
        <p class="section-label">필터</p>
        <h3>축제 검색과 상태 보기</h3>
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
      <p class="helper-text">필터 값을 입력한 뒤 검색 적용 버튼을 눌러주세요.</p>
      <div class="inline-actions">
        <button
          class="btn btn--primary btn--small"
          type="button"
          @click="emit('apply')"
        >
          검색 적용
        </button>
        <button
          class="btn btn--secondary btn--small"
          type="button"
          :class="{ 'is-active': viewMode === 'calendar' }"
          @click="emit('update:viewMode', 'calendar')"
        >
          달력
        </button>
        <button
          class="btn btn--secondary btn--small"
          type="button"
          :class="{ 'is-active': viewMode === 'list' }"
          @click="emit('update:viewMode', 'list')"
        >
          목록
        </button>
      </div>
    </div>
  </section>
</template>
