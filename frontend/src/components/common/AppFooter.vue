<script setup>
import { useRouter } from "vue-router";
import mascot from "../../assets/mascot.png";
const router = useRouter();
</script>

<template>
  <footer class="portal-footer">
    <div class="portal-footer__links">
      <div class="container">
        <button type="button" @click="router.push('/')">서울 정보</button>
        <button type="button" @click="router.push('/festivals')">축제 일정</button>
        <button type="button" @click="router.push('/posts')">커뮤니티</button>
        <span>데이터 출처 및 이용 안내</span>
      </div>
    </div>
    <div class="container portal-footer__main">
      <div class="portal-footer__brand">
        <img :src="mascot" alt="" />
        <div><strong>서울잇다</strong><p>서울의 장소, 축제, 시민 경험을 한곳에서 잇는 공공정보 허브</p></div>
      </div>
      <div class="portal-footer__info">
        <p>관광 데이터: 한국관광공사 TourAPI 4.0 · 커뮤니티: 익명 게시판</p>
        <p>본 서비스는 스타트캠프 교육 목적의 MVP입니다.</p>
        <small>© 2026 Seoul ITDA. All rights reserved.</small>
      </div>
    </div>
  </footer>
</template>
