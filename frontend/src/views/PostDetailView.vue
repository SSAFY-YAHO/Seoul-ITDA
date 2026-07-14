<script setup>
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { fetchPostById, deletePost } from "../api/posts";

const route = useRoute();
const router = useRouter();
const post = ref(null);
const loading = ref(true);
const error = ref("");
const password = ref("");
const deleting = ref(false);
const deleteError = ref("");
const deleteSuccess = ref("");

async function loadPost() {
  loading.value = true;
  error.value = "";

  try {
    post.value = await fetchPostById(route.params.id);
  } catch (err) {
    error.value = err.message || "게시글을 불러오지 못했습니다.";
  } finally {
    loading.value = false;
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
  <div class="page-shell">
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
          <p>{{ post.content || "내용이 없습니다." }}</p>
          <div class="meta-row">
            <span>조회수</span>
            <strong>{{ post.views || 0 }}</strong>
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
