<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { createPost } from "../api/posts";
import PostImageUploader from "../components/community/PostImageUploader.vue";

const router = useRouter();
const title = ref("");
const content = ref("");
const password = ref("");
const submitting = ref(false);
const error = ref("");
const imageUrls = ref([]);

async function submitPost() {
  if (!title.value.trim() || !content.value.trim() || !password.value.trim()) {
    error.value = "제목, 내용, 수정용 비밀번호를 모두 입력해주세요.";
    return;
  }

  submitting.value = true;
  error.value = "";

  try {
    const created = await createPost({
      title: title.value,
      content: content.value,
      edit_password: password.value,
      image_urls: imageUrls.value,
    });
    const postId = created?.id || created?.post_id;
    if (postId) {
      router.push(`/posts/${postId}`);
      return;
    }
    router.push("/posts");
  } catch (err) {
    error.value = err.message || "게시글을 등록하지 못했습니다.";
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <div class="page-shell community-page community-page--form">
    <section class="section-card section-block">
      <div class="section-heading">
        <div>
          <p class="section-label">글쓰기</p>
          <h2>새 게시글 작성</h2>
          <p class="page-subtitle">비밀번호는 수정·삭제 검증에만 사용됩니다.</p>
        </div>
        <button
          class="btn btn--ghost"
          type="button"
          @click="router.push('/posts')"
        >
          목록으로
        </button>
      </div>

      <div class="form-grid">
        <label class="field" for="title">
          <span>제목</span>
          <input
            id="title"
            v-model="title"
            class="input"
            placeholder="예: 서울에서 추천하는 조용한 카페"
          />
        </label>
        <label class="field" for="content">
          <span>내용</span>
          <textarea
            id="content"
            v-model="content"
            class="textarea"
            placeholder="당신의 서울 경험을 공유해보세요."
          />
        </label>
        <label class="field" for="password">
          <span>수정용 비밀번호</span>
          <input
            id="password"
            v-model="password"
            class="input"
            type="password"
            placeholder="비밀번호를 입력하세요"
          />
          <small
            >실제 개인 비밀번호를 사용하지 말고, 본인만 기억하는 간단한
            비밀번호를 입력하세요.</small
          >
        </label>
        <PostImageUploader v-model="imageUrls" />
        <p v-if="error" class="form-error">{{ error }}</p>
        <button
          class="btn btn--primary"
          type="button"
          :disabled="submitting"
          @click="submitPost"
        >
          {{ submitting ? "등록 중..." : "등록하기" }}
        </button>
      </div>
    </section>
  </div>
</template>
