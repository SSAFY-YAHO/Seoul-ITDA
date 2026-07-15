<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { fetchPosts } from "../api/posts";

const router = useRouter();
const posts = ref([]);
const loading = ref(true);
const error = ref("");
const searchInput = ref("");
const searchQuery = ref("");
const sort = ref("latest");
const currentPage = ref(1);
const pageSize = 5;

const sortedPosts = computed(() => [...posts.value].sort((a, b) => {
  if (sort.value === "views") return (b.views || 0) - (a.views || 0);
  return new Date(b.created_at || 0) - new Date(a.created_at || 0);
}));
const totalPages = computed(() => Math.max(1, Math.ceil(sortedPosts.value.length / pageSize)));
const paginatedPosts = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return sortedPosts.value.slice(start, start + pageSize);
});
const visiblePages = computed(() => {
  const start = Math.max(1, Math.min(currentPage.value - 2, totalPages.value - 4));
  const end = Math.min(totalPages.value, start + 4);
  return Array.from({ length: end - start + 1 }, (_, index) => start + index);
});
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
function submitSearch() { currentPage.value = 1; searchQuery.value = searchInput.value.trim(); loadPosts(); }
function clearSearch() { currentPage.value = 1; searchInput.value = ""; searchQuery.value = ""; loadPosts(); }
function goToPage(page) {
  currentPage.value = Math.min(Math.max(page, 1), totalPages.value);
  document.querySelector('.portal-board')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
watch(sort, () => { currentPage.value = 1; });
watch(totalPages, (pages) => { if (currentPage.value > pages) currentPage.value = pages; });
onMounted(loadPosts);
</script>

<template>
  <div class="page-shell portal-page community-page community-page--list">
    <section class="portal-page-hero">
      <div><p>SEOUL CITIZEN COMMUNITY</p><h1>시민 커뮤니티</h1><span>서울에서 발견한 장소와 경험을 로그인 없이 자유롭게 나눠보세요.</span></div>
      <button class="btn btn--primary" type="button" @click="router.push('/posts/new')">새 글 작성</button>
    </section>
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
        <button v-for="post in paginatedPosts" :key="post.id" type="button" :class="{ 'has-image': post.image_urls?.[0] }" @click="router.push(`/posts/${post.id}`)">
          <span class="portal-post-table__number">{{ String(post.id).padStart(2, '0') }}</span>
          <img v-if="post.image_urls?.[0]" class="portal-post-table__thumb" :src="post.image_urls[0]" alt="" loading="lazy" />
          <span class="portal-post-table__content"><strong>{{ post.title || '제목 없음' }}</strong><small>{{ (post.content || '내용 없음').slice(0, 90) }}</small></span>
          <span class="portal-post-table__meta">
            <small>{{ formatDate(post.created_at) }}</small>
            <span class="post-reactions"><b>♡ {{ post.likes || 0 }}</b><b>조회 {{ post.views || 0 }}</b></span>
          </span>
        </button>
      </div>
      <nav class="community-pagination" aria-label="게시글 페이지 이동">
        <button type="button" :disabled="currentPage === 1" aria-label="이전 페이지" @click="goToPage(currentPage - 1)">← 이전</button>
        <button
          v-for="page in visiblePages"
          :key="page"
          type="button"
          :class="{ active: currentPage === page }"
          :aria-current="currentPage === page ? 'page' : undefined"
          @click="goToPage(page)"
        >{{ page }}</button>
        <button type="button" :disabled="currentPage === totalPages" aria-label="다음 페이지" @click="goToPage(currentPage + 1)">다음 →</button>
      </nav>
    </section>
  </div>
</template>

<style scoped>
.portal-board { margin-top:22px; }
.portal-board__header { display:flex; justify-content:space-between; gap:20px; align-items:end; }.portal-board__header h2 { margin:0; font-family:Georgia,'Noto Serif KR',serif; font-weight:400; }.portal-board__header > span { color:#748277; font-size:12px; }
.portal-board__tools { display:flex; justify-content:space-between; gap:14px; margin:22px 0 10px; padding:15px; border-radius:18px; background:#edf3df; }.portal-board__search { display:flex; flex:1; gap:7px; }.portal-board__search input { max-width:540px; border-radius:999px; padding-inline:18px; }
.portal-post-table { overflow:hidden; margin-top:8px; border:1px solid #dce5d8; border-radius:18px; }.portal-post-table > button { display:grid; grid-template-columns:60px minmax(0,1fr) 170px; align-items:center; width:100%; padding:19px 10px; border:0; border-bottom:1px dashed #d3dfd0; background:rgba(255,255,255,.68); color:#304a39; text-align:left; transition:background .2s ease,padding-left .2s ease; }.portal-post-table > button:last-child { border-bottom:0; }.portal-post-table > button:hover { padding-left:16px; background:#f7faef; }.portal-post-table__number { display:grid; place-items:center; width:34px; height:34px; margin:auto; border-radius:50%; background:#e4efd8; color:#68806d; text-align:center; font-size:12px; }.portal-post-table__content { display:grid; gap:5px; min-width:0; }.portal-post-table__content strong,.portal-post-table__content small { overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }.portal-post-table__content small { color:#78867c; }.portal-post-table__meta { display:grid; gap:5px; color:#7d8b81; text-align:right; }.portal-post-table__meta b { color:#52705c; font-size:12px; }.post-reactions { display:flex; justify-content:flex-end; gap:11px; }.post-reactions b:first-child { color:#a95652; }
.portal-post-table > button.has-image { grid-template-columns:60px 64px minmax(0,1fr) 170px; column-gap:14px; }.portal-post-table__thumb { width:64px; height:52px; border-radius:10px; object-fit:cover; }
.community-pagination { display:flex; align-items:center; justify-content:center; gap:7px; margin-top:26px; }.community-pagination button { min-width:38px; height:38px; padding:0 12px; border:1px solid #ccd9c8; border-radius:999px; background:#fbfcf7; color:#58705f; font-weight:800; transition:.18s ease; }.community-pagination button:hover:not(:disabled) { border-color:#6d9278; background:#edf4e5; transform:translateY(-2px); }.community-pagination button.active { border-color:#3f6b52; background:#3f6b52; color:white; box-shadow:0 7px 14px rgba(49,89,65,.16); }.community-pagination button:disabled { cursor:not-allowed; opacity:.35; }
@media(max-width:640px){.portal-board__header{align-items:start;flex-direction:column}.portal-board__tools,.portal-board__search{align-items:stretch;flex-direction:column}.portal-post-table>button{grid-template-columns:1fr}.portal-post-table__number{display:none}.portal-post-table__meta{display:flex;margin-top:8px;text-align:left}.community-pagination{gap:4px}.community-pagination button{min-width:34px;height:34px;padding:0 9px;font-size:12px}}
</style>
