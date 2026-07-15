<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { fetchPosts } from "../api/posts";

const router = useRouter();
const posts = ref([]);
const loading = ref(true);
const error = ref("");
const searchInput = ref("");
const searchQuery = ref("");
const sort = ref("latest");

const sortedPosts = computed(() => [...posts.value].sort((a, b) => {
  if (sort.value === "views") return (b.views || 0) - (a.views || 0);
  return new Date(b.created_at || 0) - new Date(a.created_at || 0);
}));
const totalViews = computed(() => posts.value.reduce((sum, item) => sum + (item.views || 0), 0));

function formatDate(value) {
  if (!value) return "날짜 정보 없음";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString("ko-KR");
}

async function loadPosts() {
  loading.value = true; error.value = "";
  try {
    const data = await fetchPosts({ q: searchQuery.value });
    posts.value = Array.isArray(data) ? data : data?.items || [];
  } catch (err) { error.value = err.message || "게시글을 불러오지 못했습니다."; }
  finally { loading.value = false; }
}
function submitSearch() { searchQuery.value = searchInput.value.trim(); loadPosts(); }
function clearSearch() { searchInput.value = ""; searchQuery.value = ""; loadPosts(); }
onMounted(loadPosts);
</script>

<template>
  <div class="page-shell portal-page">
    <section class="portal-page-hero">
      <div><p>SEOUL CITIZEN COMMUNITY</p><h1>시민 커뮤니티</h1><span>서울에서 발견한 장소와 경험을 로그인 없이 자유롭게 나눠보세요.</span></div>
      <button class="btn btn--primary" type="button" @click="router.push('/posts/new')">새 글 작성</button>
    </section>
    <div class="portal-stat-grid">
      <article><small>검색된 이야기</small><strong>{{ posts.length }}</strong><span>개의 게시글</span></article>
      <article><small>누적 관심</small><strong>{{ totalViews }}</strong><span>회 조회</span></article>
      <article><small>운영 방식</small><strong>익명</strong><span>로그인 없이 참여</span></article>
    </div>
    <section class="section-card section-block portal-board">
      <header class="portal-board__header"><div><p class="section-label">시민 게시판</p><h2>서울 이야기 모아보기</h2></div><span>수정·삭제에는 작성 시 입력한 비밀번호가 필요합니다.</span></header>
      <div class="portal-board__tools">
        <div class="portal-board__search"><input v-model="searchInput" class="input" placeholder="제목 또는 내용으로 검색" @keyup.enter="submitSearch"/><button class="btn btn--primary" type="button" @click="submitSearch">검색</button><button v-if="searchQuery" class="btn btn--ghost" type="button" @click="clearSearch">초기화</button></div>
        <select v-model="sort" class="select" aria-label="정렬"><option value="latest">최신순</option><option value="views">조회순</option></select>
      </div>
      <div v-if="loading" class="loading-state"><strong>게시글을 불러오는 중입니다.</strong></div>
      <div v-else-if="error" class="error-state"><strong>목록을 불러오지 못했습니다.</strong><p>{{ error }}</p><button class="btn btn--secondary" @click="loadPosts">다시 시도</button></div>
      <div v-else-if="!sortedPosts.length" class="empty-state"><strong>검색 결과가 없습니다.</strong><p>첫 번째 서울 이야기를 남겨보세요.</p></div>
      <div v-else class="portal-post-table">
        <button v-for="post in sortedPosts" :key="post.id" type="button" @click="router.push(`/posts/${post.id}`)">
          <span class="portal-post-table__number">{{ String(post.id).padStart(2, '0') }}</span>
          <span class="portal-post-table__content"><strong>{{ post.title || '제목 없음' }}</strong><small>{{ (post.content || '내용 없음').slice(0, 90) }}</small></span>
          <span class="portal-post-table__meta"><small>{{ formatDate(post.created_at) }}</small><b>조회 {{ post.views || 0 }}</b></span>
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.portal-stat-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:18px 0; }.portal-stat-grid article { display:flex; align-items:baseline; gap:7px; padding:20px; border:1px solid #dce7ef; border-radius:10px; background:#fff; }.portal-stat-grid small { color:#718497; }.portal-stat-grid strong { margin-left:auto; color:#1686c8; font-size:28px; }.portal-stat-grid span { color:#718497; font-size:12px; }.portal-board__header { display:flex; justify-content:space-between; gap:20px; align-items:end; }.portal-board__header h2 { margin:0; }.portal-board__header > span { color:#778999; font-size:12px; }.portal-board__tools { display:flex; justify-content:space-between; gap:14px; margin:22px 0 10px; padding:15px; background:#f2f7fa; }.portal-board__search { display:flex; flex:1; gap:7px; }.portal-board__search input { max-width:540px; }.portal-post-table { border-top:2px solid #173f68; }.portal-post-table > button { display:grid; grid-template-columns:60px minmax(0,1fr) 150px; align-items:center; width:100%; padding:18px 10px; border:0; border-bottom:1px solid #e1e8ee; background:#fff; color:#243f57; text-align:left; }.portal-post-table > button:hover { background:#f3f8fb; }.portal-post-table__number { color:#8294a4; text-align:center; }.portal-post-table__content { display:grid; gap:5px; min-width:0; }.portal-post-table__content strong,.portal-post-table__content small { overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }.portal-post-table__content small { color:#788a99; }.portal-post-table__meta { display:grid; gap:4px; color:#7d8e9d; text-align:right; }.portal-post-table__meta b { color:#42627d; font-size:12px; }
@media(max-width:640px){.portal-stat-grid{grid-template-columns:1fr}.portal-board__header{align-items:start;flex-direction:column}.portal-board__tools,.portal-board__search{align-items:stretch;flex-direction:column}.portal-post-table>button{grid-template-columns:1fr}.portal-post-table__number{display:none}.portal-post-table__meta{display:flex;margin-top:8px;text-align:left}}
</style>
