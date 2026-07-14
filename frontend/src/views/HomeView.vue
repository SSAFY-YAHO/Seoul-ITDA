<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import mascot from '../assets/mascot.svg'
import { fetchLocations } from '../api/locations'
import { getHealth } from '../api/client'

const router = useRouter()
const locations = ref([])
const loading = ref(true)
const error = ref('')
const health = ref(null)

const categories = [
  { key: 'tourist', label: '관광지', tone: 'badge--blue' },
  { key: 'festival', label: '축제', tone: 'badge--yellow' },
  { key: 'restaurant', label: '맛집', tone: 'badge--mint' },
]

function getCategoryLabel(category) {
  return categories.find((item) => item.key === category)?.label || category || '정보'
}

function getCategoryTone(category) {
  return categories.find((item) => item.key === category)?.tone || 'badge--blue'
}

function formatLocationAddress(location) {
  return location.address || location.road_address || '주소 정보가 아직 제공되지 않습니다.'
}

function formatLocationDescription(location) {
  return location.description || location.summary || '상세 설명은 준비 중입니다.'
}

async function loadLocations() {
  loading.value = true
  error.value = ''

  try {
    const data = await fetchLocations()
    const items = Array.isArray(data) ? data : data?.items || []
    locations.value = items
  } catch (err) {
    error.value = err.message || '서울 정보를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

async function loadHealth() {
  try {
    health.value = await getHealth()
  } catch (err) {
    health.value = { status: 'error', message: err.message || '백엔드 연결을 확인해주세요.' }
  }
}

onMounted(() => {
  loadLocations()
  loadHealth()
})
</script>

<template>
  <div class="page-shell">
    <section class="hero-section section-card">
      <div class="hero-copy">
        <span class="badge badge--yellow">서울잇다</span>
        <h1>서울의 이야기를 발견하고 연결하세요</h1>
        <p>관광지, 축제, 맛집, 그리고 익명 커뮤니티를 한 곳에서 만나보세요.</p>
        <div class="hero-actions">
          <button class="btn btn--primary" type="button" @click="router.push('/festivals')">축제 캘린더 보기</button>
          <button class="btn btn--secondary" type="button" @click="router.push('/posts')">커뮤니티 가기</button>
        </div>
        <div class="hero-highlights">
          <div class="highlight-pill">실시간 서울 정보</div>
          <div class="highlight-pill">익명 커뮤니티</div>
          <div class="highlight-pill">AI 챗봇</div>
        </div>
      </div>
      <div class="hero-visual">
        <img :src="mascot" alt="서울잇다 마스코트" />
      </div>
    </section>

    <section class="section-card section-block">
      <div class="section-heading">
        <div>
          <p class="section-label">카테고리</p>
          <h2>서울을 주제로 한 정보들</h2>
        </div>
      </div>
      <div class="category-grid">
        <div v-for="category in categories" :key="category.key" class="category-card">
          <span :class="['badge', category.tone]">{{ category.label }}</span>
          <p>{{ category.key === 'tourist' ? '도심 속 숨은 명소와 역사 문화 코스를 확인하세요.' : category.key === 'festival' ? '시즌별 축제와 행사 정보를 빠르게 살펴보세요.' : '서울 맛집과 분위기 좋은 식당을 둘러보세요.' }}</p>
        </div>
      </div>
    </section>

    <section class="section-card section-block">
      <div class="section-heading">
        <div>
          <p class="section-label">서울 정보</p>
          <h2>지역 정보 카드</h2>
        </div>
        <button class="btn btn--ghost" type="button" @click="router.push('/posts')">커뮤니티 보기</button>
      </div>

      <div v-if="loading" class="loading-state">
        <strong>서울 정보를 불러오는 중입니다.</strong>
        <p>잠시만 기다려 주세요.</p>
      </div>
      <div v-else-if="error" class="error-state">
        <strong>서울 정보를 불러오지 못했습니다.</strong>
        <p>{{ error }}</p>
        <button class="btn btn--secondary" type="button" @click="loadLocations">다시 시도</button>
      </div>
      <div v-else-if="locations.length === 0" class="empty-state">
        <strong>표시할 서울 정보가 없습니다.</strong>
        <p>백엔드에 지역 정보가 준비되면 여기에서 확인할 수 있습니다.</p>
      </div>
      <div v-else class="card-list">
        <article v-for="location in locations" :key="location.id || location.name" class="location-card">
          <div class="location-card__header">
            <span :class="['badge', getCategoryTone(location.category)]">{{ getCategoryLabel(location.category) }}</span>
            <h3>{{ location.name || location.title || '이름 미정' }}</h3>
          </div>
          <p>{{ formatLocationDescription(location) }}</p>
          <p class="helper-text">{{ formatLocationAddress(location) }}</p>
          <div v-if="location.operating_hours" class="meta-row">
            <span>운영 정보</span>
            <strong>{{ location.operating_hours }}</strong>
          </div>
        </article>
      </div>
    </section>

    <section class="section-card section-block">
      <div class="section-heading">
        <div>
          <p class="section-label">이번 달 축제</p>
          <h2>서울 축제 미리보기</h2>
        </div>
        <button class="btn btn--ghost btn--small" type="button" @click="router.push('/festivals')">캘린더 전체 보기</button>
      </div>
      <div class="ai-card">
        <div class="ai-card__title">
          <span class="badge badge--orange">AI 추천</span>
          <h3>이번 달 서울 축제를 미리 둘러보세요</h3>
        </div>
        <p>축제 캘린더 페이지에서 월별 일정과 상세 정보를 확인할 수 있습니다.</p>
        <p class="helper-text">현재 저장소의 축제 데이터가 준비되면 자동으로 반영됩니다.</p>
      </div>
    </section>

    <section class="section-card section-block">
      <div class="section-heading">
        <div>
          <p class="section-label">커뮤니티</p>
          <h2>익명으로 나누는 서울 이야기</h2>
        </div>
        <button class="btn btn--primary" type="button" @click="router.push('/posts')">게시글 보기</button>
      </div>
      <p class="helper-text">현재 백엔드에 게시글 API가 아직 없으므로, 이 화면은 목록 진입과 안내 문구 중심으로 구성했습니다. 게시글 기능이 준비되면 바로 연결됩니다.</p>
    </section>

    <section class="section-card section-block" v-if="health">
      <div class="section-heading">
        <div>
          <p class="section-label">백엔드 상태</p>
          <h2>연결 상태 확인</h2>
        </div>
      </div>
      <div class="health-panel">
        <strong>{{ health.status === 'ok' ? '백엔드 연결이 정상입니다.' : '백엔드 연결을 확인해 주세요.' }}</strong>
        <p>{{ health.message || 'FastAPI health endpoint가 응답하고 있습니다.' }}</p>
      </div>
    </section>
  </div>
</template>