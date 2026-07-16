<script setup>
import { RouterLink } from "vue-router";
import { Capacitor } from "@capacitor/core";

const isNativeApp = Capacitor.isNativePlatform();

const developers = (import.meta.env.VITE_DEVELOPERS || "")
  .split(",")
  .map((name) => name.trim())
  .filter(Boolean);
</script>

<template>
  <footer class="app-footer">
    <div class="container app-footer__inner story-footer">
      <div class="story-footer__brand">
        <strong>Seoul ITDA</strong>
        <p>서울의 장소와 축제, 사람의 이야기를 다정하게 잇습니다.</p>
      </div>

      <nav class="story-footer__group" aria-label="푸터 메뉴">
        <b>메뉴</b>
        <ul class="story-footer__links">
          <li><RouterLink to="/">홈</RouterLink></li>
          <li><RouterLink to="/festivals">축제 캘린더</RouterLink></li>
          <li><RouterLink to="/posts">커뮤니티</RouterLink></li>
          <li v-if="!isNativeApp"><RouterLink to="/download">Android 앱</RouterLink></li>
        </ul>
      </nav>

      <div class="story-footer__group">
        <b>Developer</b>
        <ul v-if="developers.length" class="story-footer__developers" aria-label="개발자 목록">
          <li v-for="developer in developers" :key="developer">{{ developer }}</li>
        </ul>
        <p v-else>개발자 정보가 등록되지 않았습니다.</p>
      </div>

      <div class="story-footer__group">
        <b>Contact</b>
        <p>Seoul, Republic of Korea<br />hello@seoul-itda.kr</p>
      </div>
    </div>
  </footer>
</template>
