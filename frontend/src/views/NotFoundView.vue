<script setup>
import { useRouter } from "vue-router";

const router = useRouter();
</script>

<template>
  <div class="page-shell">
    <section class="section-card section-block not-found">
      <h2>페이지를 찾을 수 없습니다.</h2>
      <p>요청하신 주소는 존재하지 않거나, 지금은 준비 중일 수 있습니다.</p>
      <button class="btn btn--primary" type="button" @click="router.push('/')">
        홈으로 돌아가기
      </button>
    </section>
  </div>
</template>
