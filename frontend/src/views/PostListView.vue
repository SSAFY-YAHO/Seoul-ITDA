<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { fetchPosts } from "../api/posts";

const router = useRouter();
const posts = ref([]);
const loading = ref(true);
const error = ref("");
const searchQuery = ref("");
const searchInput = ref("");

async function loadPosts() {
  loading.value = true;
  error.value = "";

  try {
    const data = await fetchPosts({ q: searchQuery.value });
    const items = Array.isArray(data) ? data : data?.items || [];
    posts.value = items;
  } catch (err) {
    error.value = err.message || "게시글을 불러오지 못했습니다.";
  } finally {
    loading.value = false;
  }
}

function submitSearch() {
  searchQuery.value = searchInput.value.trim();
  loadPosts();
}

function clearSearch() {
  searchInput.value = "";
  searchQuery.value = "";
  loadPosts();
}

const hasPosts = computed(() => posts.value.length > 0);

onMounted(() => {
  loadPosts();
});
</script>

<template>
  <div class="page-shell">
    <section class="section-card section-block">
      <div class="section-heading">
        <div>
          <p class="section-label">커뮤니티</p>
          <h2>익명 게시글</h2>
          <p class="page-subtitle">
            로그인 없이 제목과 내용으로 소중한 경험을 나눠보세요.
          </p>
        </div>
        <button
          class="btn btn--primary"
          type="button"
          @click="router.push('/posts/new')"
        >
          글쓰기
        </button>
      </div>

      <div class="search-row">
        <label class="sr-only" for="post-search">게시글 검색</label>
        <input
          id="post-search"
          v-model="searchInput"
          class="input"
          placeholder="제목이나 내용을 검색해보세요"
          @keyup.enter="submitSearch"
        />
        <button class="btn btn--secondary" type="button" @click="submitSearch">
          검색
        </button>
        <button
          v-if="searchQuery"
          class="btn btn--ghost"
          type="button"
          @click="clearSearch"
        >
          초기화
        </button>
      </div>

      <div v-if="loading" class="loading-state">
        <strong>게시글을 불러오는 중입니다.</strong>
        <p>잠시만 기다려 주세요.</p>
      </div>
      <div v-else-if="error" class="error-state">
        <strong>게시글 목록을 불러오지 못했습니다.</strong>
        <p>{{ error }}</p>
        <button class="btn btn--secondary" type="button" @click="loadPosts">
          다시 시도
        </button>
      </div>
      <div v-else-if="!hasPosts" class="empty-state">
        <strong>아직 게시글이 없습니다.</strong>
        <p>첫 번째 글을 남겨보세요.</p>
      </div>
      <div v-else class="card-list card-list--stacked">
        <article
          v-for="post in posts"
          :key="post.id"
          class="post-card"
          @click="router.push(`/posts/${post.id}`)"
        >
          <div class="post-card__top">
            <span class="badge badge--yellow">익명</span>
            <span class="meta-pill">조회 {{ post.views || 0 }}</span>
          </div>
          <h3>{{ post.title || "제목 없음" }}</h3>
          <p>{{ post.content || "내용이 없습니다." }}</p>
          <div class="post-card__footer">
            <span>{{ post.created_at || "작성일 없음" }}</span>
            <button
              class="btn btn--ghost btn--small"
              type="button"
              @click.stop="router.push(`/posts/${post.id}`)"
            >
              자세히 보기
            </button>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>
