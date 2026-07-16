<script setup>
import brandMark from "../assets/mascot.png";

const apkUrl = "/downloads/seoul-itda.apk";

const installSteps = [
  {
    number: "01",
    title: "APK 내려받기",
    description: "Android 휴대폰에서 다운로드 버튼을 눌러 설치 파일을 받아주세요.",
  },
  {
    number: "02",
    title: "설치 권한 허용",
    description: "안내가 나타나면 사용 중인 브라우저의 ‘알 수 없는 앱 설치’를 허용해주세요.",
  },
  {
    number: "03",
    title: "서울잇다 시작하기",
    description: "다운로드한 APK 파일을 열어 설치한 뒤 서울의 오늘을 만나보세요.",
  },
];
</script>

<template>
  <div class="page-shell android-download-page">
    <section class="android-download-hero">
      <div class="android-download-hero__copy">
        <p class="section-label">SEOUL ITDA FOR ANDROID</p>
        <h1>서울의 오늘을<br /><em>앱으로 이어보세요</em></h1>
        <p class="android-download-hero__description">
          장소 탐색부터 축제 일정, 시민들의 이야기와 AI 안내까지.<br />
          서울잇다의 모든 기능을 Android 앱에서 편하게 이용할 수 있어요.
        </p>

        <div class="android-download-hero__actions">
          <a class="btn btn--primary android-download-button" :href="apkUrl" download>
            <span class="android-download-button__icon" aria-hidden="true">↓</span>
            Android APK 다운로드
          </a>
          <span class="android-download-version">Android 전용 · 무료 설치</span>
        </div>

        <ul class="android-download-benefits" aria-label="앱 주요 특징">
          <li>서울 장소 탐색</li>
          <li>축제 일정 확인</li>
          <li>커뮤니티와 AI 안내</li>
        </ul>
      </div>

      <div class="android-download-hero__visual" aria-hidden="true">
        <span class="android-download-spark android-download-spark--one">✦</span>
        <span class="android-download-spark android-download-spark--two">✦</span>
        <div class="android-phone">
          <div class="android-phone__speaker"></div>
          <div class="android-phone__screen">
            <span class="android-phone__eyebrow">SEOUL ITDA</span>
            <img :src="brandMark" alt="" />
            <strong>서울잇다</strong>
            <small>서울을 발견하고, 경험을 잇다</small>
          </div>
        </div>
      </div>
    </section>

    <section class="android-install-section" aria-labelledby="android-install-title">
      <div class="android-install-heading">
        <div>
          <p class="section-label">HOW TO INSTALL</p>
          <h2 id="android-install-title">3단계면 설치가 끝나요</h2>
        </div>
        <p>Play 스토어를 거치지 않고 APK 파일로 직접 설치합니다.</p>
      </div>

      <ol class="android-install-steps">
        <li v-for="step in installSteps" :key="step.number">
          <span>{{ step.number }}</span>
          <div>
            <strong>{{ step.title }}</strong>
            <p>{{ step.description }}</p>
          </div>
        </li>
      </ol>

      <div class="android-security-note">
        <span aria-hidden="true">✓</span>
        <p>
          <strong>안심하고 설치하세요.</strong>
          Android의 보안 경고는 스토어 외부 앱을 설치할 때 표시되는 기본 안내입니다.
          이 페이지에서 받은 파일인지 확인한 후 설치해주세요.
        </p>
      </div>
    </section>
  </div>
</template>
