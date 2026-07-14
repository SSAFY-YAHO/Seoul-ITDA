<script setup>
import { ref } from 'vue'
import { apiBaseUrl, fetchHealth } from '../services/api'

const healthState = ref('아직 확인하지 않음')
const healthPayload = ref('')
const isChecking = ref(false)

async function checkBackend() {
  isChecking.value = true
  healthState.value = '확인 중'

  try {
    const payload = await fetchHealth()
    healthState.value = '연결 성공'
    healthPayload.value = JSON.stringify(payload, null, 2)
  } catch (error) {
    healthState.value = '연결 실패'
    healthPayload.value = error instanceof Error ? error.message : '알 수 없는 오류'
  } finally {
    isChecking.value = false
  }
}
</script>

<template>
  <section class="dashboard">
    <article class="hero-card">
      <p class="hero-card__lead">
        지금 단계는 기능 구현 전 초기세팅입니다. 프론트와 백엔드가 같은 규칙으로 동작하도록
        폴더 구조, 환경변수, 기본 라우팅, DB 설정, 상태 확인 API를 먼저 고정해둔 상태입니다.
      </p>

      <div class="hero-card__grid">
        <div class="info-card">
          <span>Frontend</span>
          <strong>Vue 3 + Vite</strong>
          <p>SPA 구조와 라우터, API 서비스 레이어를 미리 분리했습니다.</p>
        </div>
        <div class="info-card">
          <span>Backend</span>
          <strong>FastAPI + SQLAlchemy</strong>
          <p>SQLite 연결과 CORS 설정, 기본 엔드포인트가 준비되어 있습니다.</p>
        </div>
        <div class="info-card">
          <span>Environment</span>
          <strong>.env 중심 설정</strong>
          <p>실제 키는 `.env`, 저장소에는 `.env.example`만 유지합니다.</p>
        </div>
      </div>
    </article>

    <section class="section">
      <div class="section-header">
        <div>
          <h2>초기 작업 상태</h2>
          <p>기능 개발 전에 바로 확인할 수 있는 공통 베이스입니다.</p>
        </div>
        <span class="section-badge">Scaffold Ready</span>
      </div>

      <div class="status-grid">
        <div class="status-card">
          <span>Community</span>
          <strong>예정</strong>
          <p>익명 게시판 CRUD, 검색, 조회수 기능은 다음 단계에서 추가합니다.</p>
        </div>
        <div class="status-card">
          <span>Chat</span>
          <strong>예정</strong>
          <p>서울 JSON과 커뮤니티 데이터를 연결한 `POST /api/chat`을 이후 구현합니다.</p>
        </div>
        <div class="status-card">
          <span>Data</span>
          <strong>수용 준비</strong>
          <p>`data/`와 `backend/app/services/`에 적재 및 정제 로직을 붙일 수 있게 비워뒀습니다.</p>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="section-header">
        <div>
          <h2>백엔드 연결 확인</h2>
          <p>프론트에서 FastAPI가 뜨는지 즉시 확인할 수 있습니다.</p>
        </div>
      </div>

      <div class="status-grid">
        <div class="api-card">
          <span>API Base URL</span>
          <strong>{{ apiBaseUrl }}</strong>
          <p>`.env`의 `VITE_API_BASE_URL`로 변경할 수 있습니다.</p>
          <code>GET /api/health</code>
        </div>
        <div class="api-card">
          <span>Health State</span>
          <strong>{{ healthState }}</strong>
          <p>버튼을 눌러 현재 백엔드 응답을 확인하세요.</p>
        </div>
        <div class="api-card">
          <span>Next Step</span>
          <strong>기능 개발 시작</strong>
          <p>이 상태에서 게시판 모델, 라우터, 뷰를 차례대로 확장하면 됩니다.</p>
        </div>
      </div>

      <div class="health-banner">
        <div>
          <strong>FastAPI 상태 체크</strong>
          <pre>{{ healthPayload || '아직 요청 결과가 없습니다.' }}</pre>
        </div>
        <button type="button" :disabled="isChecking" @click="checkBackend">
          {{ isChecking ? '확인 중...' : '연결 확인' }}
        </button>
      </div>
    </section>
  </section>
</template>