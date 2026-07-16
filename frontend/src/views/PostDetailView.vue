<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  createComment,
  deletePost,
  fetchComments,
  fetchPostById,
  likeComment,
  likePost,
} from "../api/posts";

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
const comments = ref([]);
const commentsLoading = ref(false);
const commentError = ref("");
const commentAuthor = ref("");
const commentContent = ref("");
const commentSubmitting = ref(false);
const likingCommentId = ref(null);
const replyToCommentId = ref(null);
const replyAuthor = ref("");
const replyContent = ref("");
const replySubmitting = ref(false);

const topLevelComments = computed(() => comments.value.filter((comment) => !comment.parent_id));

function likeStorageKey() {
  return `seoul-itda-liked-post-${route.params.id}`;
}

function commentLikeStorageKey(commentId) {
  return `seoul-itda-liked-comment-${commentId}`;
}

function hasLikedComment(commentId) {
  return localStorage.getItem(commentLikeStorageKey(commentId)) === "true";
}

function formatCommentDate(value) {
  if (!value) return "작성일 없음";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString("ko-KR");
}

function repliesFor(commentId) {
  return comments.value.filter((comment) => comment.parent_id === commentId);
}

function startReply(comment) {
  replyToCommentId.value = comment.id;
  replyAuthor.value = commentAuthor.value.trim();
  replyContent.value = "";
  commentError.value = "";
}

function cancelReply() {
  replyToCommentId.value = null;
  replyContent.value = "";
}

async function loadComments() {
  commentsLoading.value = true;
  commentError.value = "";
  try {
    const data = await fetchComments(route.params.id);
    comments.value = Array.isArray(data?.items) ? data.items : [];
  } catch (err) {
    commentError.value = err.message || "댓글을 불러오지 못했습니다.";
  } finally {
    commentsLoading.value = false;
  }
}

async function loadPost() {
  loading.value = true;
  error.value = "";

  try {
    post.value = await fetchPostById(route.params.id);
    hasLiked.value = localStorage.getItem(likeStorageKey()) === "true";
    await loadComments();
  } catch (err) {
    error.value = err.message || "게시글을 불러오지 못했습니다.";
  } finally {
    loading.value = false;
  }
}

async function handleCreateComment() {
  const author = commentAuthor.value.trim();
  const content = commentContent.value.trim();
  if (!author || !content) {
    commentError.value = "닉네임과 댓글 내용을 모두 입력해주세요.";
    return;
  }

  commentSubmitting.value = true;
  commentError.value = "";
  try {
    const created = await createComment(route.params.id, { author, content });
    comments.value.push(created);
    commentContent.value = "";
  } catch (err) {
    commentError.value = err.message || "댓글을 등록하지 못했습니다.";
  } finally {
    commentSubmitting.value = false;
  }
}

async function handleCreateReply(parentId) {
  const author = replyAuthor.value.trim();
  const content = replyContent.value.trim();
  if (!author || !content) {
    commentError.value = "닉네임과 답글 내용을 모두 입력해주세요.";
    return;
  }

  replySubmitting.value = true;
  commentError.value = "";
  try {
    const created = await createComment(route.params.id, {
      author,
      content,
      parent_id: parentId,
    });
    comments.value.push(created);
    replyToCommentId.value = null;
    replyContent.value = "";
  } catch (err) {
    commentError.value = err.message || "답글을 등록하지 못했습니다.";
  } finally {
    replySubmitting.value = false;
  }
}

async function handleCommentLike(comment) {
  if (hasLikedComment(comment.id) || likingCommentId.value !== null) return;
  likingCommentId.value = comment.id;
  commentError.value = "";
  try {
    const liked = await likeComment(route.params.id, comment.id);
    const index = comments.value.findIndex((item) => item.id === comment.id);
    if (index >= 0) comments.value[index] = liked;
    localStorage.setItem(commentLikeStorageKey(comment.id), "true");
  } catch (err) {
    commentError.value = err.message || "댓글 좋아요를 반영하지 못했습니다.";
  } finally {
    likingCommentId.value = null;
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

        <section class="comments-card" aria-labelledby="comments-title">
          <div class="comments-card__heading">
            <div>
              <p class="section-label">COMMENTS</p>
              <h3 id="comments-title">댓글 {{ comments.length }}</h3>
            </div>
            <button class="btn btn--ghost btn--small" type="button" :disabled="commentsLoading" @click="loadComments">
              새로고침
            </button>
          </div>

          <form class="comment-form" @submit.prevent="handleCreateComment">
            <label class="field">
              <span>닉네임</span>
              <input v-model="commentAuthor" class="input" maxlength="30" placeholder="닉네임을 입력하세요" />
            </label>
            <label class="field">
              <span>댓글</span>
              <textarea v-model="commentContent" class="textarea textarea--compact" maxlength="1000" placeholder="서울 여행 이야기를 나눠보세요"></textarea>
            </label>
            <div class="comment-form__footer">
              <small>{{ commentContent.length }} / 1000</small>
              <button class="btn btn--primary" type="submit" :disabled="commentSubmitting">
                {{ commentSubmitting ? "등록 중..." : "댓글 등록" }}
              </button>
            </div>
          </form>

          <p v-if="commentError" class="form-error">{{ commentError }}</p>
          <div v-if="commentsLoading" class="loading-state">댓글을 불러오는 중입니다.</div>
          <div v-else-if="comments.length === 0" class="empty-state">첫 댓글을 남겨보세요.</div>
          <ul v-else class="comment-list">
            <li v-for="comment in topLevelComments" :key="comment.id" class="comment-thread">
              <article class="comment-item">
                <div class="comment-item__meta">
                  <strong>{{ comment.author }}</strong>
                  <time :datetime="comment.created_at">{{ formatCommentDate(comment.created_at) }}</time>
                </div>
                <p>{{ comment.content }}</p>
                <div class="comment-item__actions">
                  <button
                    class="comment-like-button"
                    :class="{ 'comment-like-button--active': hasLikedComment(comment.id) }"
                    type="button"
                    :disabled="hasLikedComment(comment.id) || likingCommentId !== null"
                    @click="handleCommentLike(comment)"
                  >
                    {{ hasLikedComment(comment.id) ? "♥" : "♡" }} 좋아요 {{ comment.likes || 0 }}
                  </button>
                  <button class="comment-reply-button" type="button" @click="startReply(comment)">↳ 답글</button>
                </div>
              </article>

              <form
                v-if="replyToCommentId === comment.id"
                class="reply-form"
                @submit.prevent="handleCreateReply(comment.id)"
              >
                <strong>{{ comment.author }}님에게 답글</strong>
                <input v-model="replyAuthor" class="input" maxlength="30" placeholder="닉네임" />
                <textarea v-model="replyContent" class="textarea textarea--compact" maxlength="1000" placeholder="답글을 입력하세요"></textarea>
                <div class="reply-form__actions">
                  <button class="btn btn--ghost btn--small" type="button" @click="cancelReply">취소</button>
                  <button class="btn btn--primary btn--small" type="submit" :disabled="replySubmitting">
                    {{ replySubmitting ? "등록 중..." : "답글 등록" }}
                  </button>
                </div>
              </form>

              <ul v-if="repliesFor(comment.id).length" class="reply-list">
                <li v-for="reply in repliesFor(comment.id)" :key="reply.id" class="comment-item comment-item--reply">
                  <div class="comment-item__meta">
                    <strong>↳ {{ reply.author }}</strong>
                    <time :datetime="reply.created_at">{{ formatCommentDate(reply.created_at) }}</time>
                  </div>
                  <p>{{ reply.content }}</p>
                  <button
                    class="comment-like-button"
                    :class="{ 'comment-like-button--active': hasLikedComment(reply.id) }"
                    type="button"
                    :disabled="hasLikedComment(reply.id) || likingCommentId !== null"
                    @click="handleCommentLike(reply)"
                  >
                    {{ hasLikedComment(reply.id) ? "♥" : "♡" }} 좋아요 {{ reply.likes || 0 }}
                  </button>
                </li>
              </ul>
            </li>
          </ul>
        </section>

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
.comments-card { display:grid; gap:20px; margin-top:24px; padding:clamp(20px,4vw,32px); border:1px solid #d8e2d3; border-radius:18px; background:#fffefa; }
.comments-card__heading,.comment-form__footer,.comment-item__meta { display:flex; align-items:center; justify-content:space-between; gap:14px; }
.comments-card__heading h3 { margin:0; color:#315640; font-size:1.35rem; }
.comment-form { display:grid; gap:14px; padding:18px; border-radius:15px; background:#f4f7ed; }
.comment-form__footer small { color:var(--color-text-sub); }
.comment-list { display:grid; gap:12px; margin:0; padding:0; list-style:none; }
.comment-thread { display:grid; gap:10px; }
.comment-item { display:grid; gap:10px; padding:18px; border:1px solid #e0e7dc; border-radius:15px; background:white; }
.comment-item__meta strong { color:#315640; }.comment-item__meta time { color:var(--color-text-sub); font-size:.78rem; }
.comment-item p { margin:0; color:var(--color-text-main); line-height:1.65; white-space:pre-wrap; overflow-wrap:anywhere; }
.comment-like-button { justify-self:start; padding:7px 11px; border-radius:999px; background:#fff5f2; color:#a9514d; font-size:.78rem; font-weight:800; }
.comment-like-button:hover:not(:disabled) { background:#fde8e3; }.comment-like-button--active { background:#fde8e3; }.comment-like-button:disabled { cursor:default; opacity:1; }
.comment-item__actions,.reply-form__actions { display:flex; align-items:center; gap:8px; }
.comment-reply-button { padding:7px 11px; border-radius:999px; background:#eef4e9; color:#456650; font-size:.78rem; font-weight:800; }
.reply-form { display:grid; gap:10px; margin-left:28px; padding:16px; border-left:3px solid #9bb594; border-radius:0 14px 14px 0; background:#f4f7ed; }
.reply-form > strong { color:#456650; font-size:.82rem; }.reply-form__actions { justify-content:flex-end; }
.reply-list { display:grid; gap:9px; margin:0 0 0 28px; padding:0; list-style:none; }
.comment-item--reply { border-left:3px solid #a9bfa3; background:#f9fbf5; }
@media(max-width:640px){.post-image-gallery{grid-template-columns:1fr}.post-image-gallery a:first-child:nth-last-child(1){grid-column:auto;aspect-ratio:4/3}}
</style>
