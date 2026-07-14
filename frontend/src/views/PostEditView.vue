<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { fetchPostById, updatePost } from "../api/posts";

const route = useRoute();
const router = useRouter();
const title = ref("");
const content = ref("");
const password = ref("");
const loading = ref(true);
const submitting = ref(false);
const error = ref("");
const postId = computed(() => route.params.id);

async function loadPost() {
  loading.value = true;
  error.value = "";

  try {
    const data = await fetchPostById(postId.value);
    title.value = data?.title || "";
    content.value = data?.content || "";
  } catch (err) {
    error.value = err.message || "게시글 정보를 불러오지 못했습니다.";
  } finally {
    loading.value = false;
  }
}

async function submitEdit() {
  if (!title.value.trim() || !content.value.trim() || !password.value.trim()) {
    error.value = "제목, 내용, 수정용 비밀번호를 모두 입력해주세요.";
    return;
  }

  submitting.value = true;
  error.value = "";

  try {
    await updatePost(postId.value, {
      title: title.value,
      content: content.value,
      password: password.value,
    });
    router.push(`/posts/${postId.value}`);
  } catch (err) {
    error.value = err.message || "게시글을 수정하지 못했습니다.";
  } finally {
    submitting.value = false;
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
        <strong>게시글 정보를 불러오는 중입니다.</strong>
        <p>잠시만 기다려 주세요.</p>
      </div>
      <div v-else>
        <div class="section-heading">
          <div>
            <p class="section-label">수정</p>
            <h2>게시글 수정</h2>
            <p class="page-subtitle">비밀번호가 맞아야 수정이 반영됩니다.</p>
          </div>
          <button
            class="btn btn--ghost"
            type="button"
            @click="router.push(`/posts/${postId}`)"
          >
            상세 보기
          </button>
        </div>

        <div class="form-grid">
          <label class="field" for="edit-title">
            <span>제목</span>
            <input
              id="edit-title"
              v-model="title"
              class="input"
              placeholder="제목을 입력하세요"
            />
          </label>
          <label class="field" for="edit-content">
            <span>내용</span>
            <textarea
              id="edit-content"
              v-model="content"
              class="textarea"
              placeholder="내용을 입력하세요"
            />
          </label>
          <label class="field" for="edit-password">
            <span>수정용 비밀번호</span>
            <input
              id="edit-password"
              v-model="password"
              class="input"
              type="password"
              placeholder="비밀번호를 입력하세요"
            />
          </label>
          <p v-if="error" class="form-error">{{ error }}</p>
          <button
            class="btn btn--primary"
            type="button"
            :disabled="submitting"
            @click="submitEdit"
          >
            {{ submitting ? "수정 중..." : "수정하기" }}
          </button>
        </div>
      </div>
    </section>
  </div>
</template>
