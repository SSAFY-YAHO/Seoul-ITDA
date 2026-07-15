<script setup>
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { fetchPostById, deletePost, likePost } from "../api/posts";

const route = useRoute();
const router = useRouter();
const post = ref(null);
const loading = ref(true);
const error = ref("");
const password = ref("");
const deleting = ref(false);
const deleteError = ref("");
const deleteSuccess = ref("");
const liking = ref(false);
const likeError = ref("");
const hasLiked = ref(false);

function likeStorageKey() {
  return `seoul-itda-liked-post-${route.params.id}`;
}

async function loadPost() {
  loading.value = true;
  error.value = "";

  try {
    post.value = await fetchPostById(route.params.id);
    hasLiked.value = localStorage.getItem(likeStorageKey()) === "true";
  } catch (err) {
    error.value = err.message || "게시글을 불러오지 못했습니다.";
  } finally {
    loading.value = false;
  }
}

async function handleLike() {
  if (hasLiked.value || liking.value) return;
  liking.value = true;
  likeError.value = "";
  try {
    post.value = await likePost(route.params.id);
    hasLiked.value = true;
    localStorage.setItem(likeStorageKey(), "true");
  } catch (err) {
    likeError.value = err.message || "좋아요를 반영하지 못했습니다.";
  } finally {
    liking.value = false;
  }
}

async function handleDelete() {
  if (!password.value.trim()) {
    deleteError.value = "수정용 비밀번호를 입력해주세요.";
    return;
  }

  deleting.value = true;
  deleteError.value = "";
  deleteSuccess.value = "";

  try {
    await deletePost(route.params.id, { edit_password: password.value });
    deleteSuccess.value = "게시글이 삭제되었습니다.";
    router.push("/posts");
  } catch (err) {
    deleteError.value = err.message || "삭제하지 못했습니다.";
  } finally {
    deleting.value = false;
  }
}

onMounted(() => {
  loadPost();
});
</script>

<template>
  <div class="page-shell community-page community-page--detail">
    <section class="section-card section-block">
      <div v-if="loading" class="loading-state">
        <strong>게시글을 불러오는 중입니다.</strong>
        <p>잠시만 기다려 주세요.</p>
      </div>
      <div v-else-if="error" class="error-state">
        <strong>게시글을 표시할 수 없습니다.</strong>
        <p>{{ error }}</p>
        <button class="btn btn--secondary" type="button" @click="loadPost">
          다시 시도
        </button>
      </div>
      <div v-else-if="!post" class="empty-state">
        <strong>게시글을 찾을 수 없습니다.</strong>
        <p>삭제되었거나 주소가 올바르지 않을 수 있습니다.</p>
      </div>
      <div v-else>
        <div class="section-heading">
          <div>
            <p class="section-label">게시글 상세</p>
            <h2>{{ post.title || "제목 없음" }}</h2>
            <p class="page-subtitle">{{ post.created_at || "작성일 없음" }}</p>
          </div>
          <div class="inline-actions">
            <button
              class="btn btn--secondary"
              type="button"
              @click="router.push('/posts')"
            >
              목록
            </button>
            <button
              class="btn btn--ghost"
              type="button"
              @click="router.push(`/posts/${post.id}/edit`)"
            >
              수정
            </button>
          </div>
        </div>

        <div class="detail-card">
          <div v-if="post.image_urls?.length" class="post-image-gallery">
            <a v-for="(url,index) in post.image_urls" :key="url" :href="url" target="_blank" rel="noopener noreferrer">
              <img :src="url" :alt="`게시글 첨부 사진 ${index + 1}`" loading="lazy" />
            </a>
          </div>
          <p>{{ post.content || "내용이 없습니다." }}</p>
          <div class="meta-row">
            <span>조회수</span>
            <strong>{{ post.views || 0 }}</strong>
          </div>
          <div class="post-like-row">
            <button
              class="post-like-button"
              :class="{ 'post-like-button--active': hasLiked }"
              type="button"
              :disabled="hasLiked || liking"
              @click="handleLike"
            >
              <span aria-hidden="true">{{ hasLiked ? "♥" : "♡" }}</span>
              {{ liking ? "반영 중" : hasLiked ? "좋아요 완료" : "좋아요" }}
              <strong>{{ post.likes || 0 }}</strong>
            </button>
            <p v-if="likeError" class="form-error">{{ likeError }}</p>
          </div>
          <div v-if="post.additional_info" class="meta-row">
            <span>추가 정보</span>
            <strong>{{ post.additional_info }}</strong>
          </div>
        </div>

        <div class="detail-card detail-card--compact">
          <h3>삭제하기</h3>
          <p class="helper-text">
            작성할 때 정한 비밀번호를 입력하면 글을 삭제할 수 있습니다.
            개인정보를 포함하지 않은 비밀번호를 사용해 주세요.
          </p>
          <label class="field" for="delete-password">
            <span>수정용 비밀번호</span>
            <input
              id="delete-password"
              v-model="password"
              class="input"
              type="password"
              placeholder="비밀번호를 입력하세요"
            />
          </label>
          <div class="inline-actions">
            <button
              class="btn btn--primary"
              type="button"
              :disabled="deleting"
              @click="handleDelete"
            >
              {{ deleting ? "삭제 중..." : "삭제" }}
            </button>
          </div>
          <p v-if="deleteError" class="form-error">{{ deleteError }}</p>
          <p v-if="deleteSuccess" class="form-success">{{ deleteSuccess }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.post-like-row { display:flex; align-items:center; gap:12px; margin-top:26px; padding-top:22px; border-top:1px dashed #cfdbc9; }
.post-like-button { display:inline-flex; align-items:center; gap:8px; padding:11px 17px; border:1px solid #e3b7b2; border-radius:999px; background:#fff8f5; color:#a9514d; font-weight:850; transition:.2s ease; }
.post-like-button:hover:not(:disabled) { transform:translateY(-2px); background:#fff0ec; box-shadow:0 8px 18px rgba(169,81,77,.12); }
.post-like-button > span { font-size:20px; line-height:1; }.post-like-button strong { min-width:22px; padding:2px 7px; border-radius:999px; background:rgba(169,81,77,.1); text-align:center; }
.post-like-button--active { border-color:#dca09a; background:#fde9e5; color:#a44540; }.post-like-button:disabled { cursor:default; opacity:1; }
.post-like-row .form-error { margin:0; }
.post-image-gallery { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; margin-bottom:28px; }.post-image-gallery a { overflow:hidden; aspect-ratio:4/3; border-radius:15px; background:#e6ecdf; }.post-image-gallery a:first-child:nth-last-child(1) { grid-column:1/-1; aspect-ratio:16/8; }.post-image-gallery img { width:100%; height:100%; object-fit:cover; transition:transform .25s ease; }.post-image-gallery a:hover img { transform:scale(1.025); }
@media(max-width:640px){.post-image-gallery{grid-template-columns:1fr}.post-image-gallery a:first-child:nth-last-child(1){grid-column:auto;aspect-ratio:4/3}}
</style>
