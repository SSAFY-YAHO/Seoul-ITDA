<script setup>
const apkUrl = "/downloads/seoul-itda.apk";
</script>

<template>
  <div class="page-shell android-download-page">
    <section class="section-card android-download-card">
      <div>
        <p class="section-label">ANDROID APP</p>
        <h1>서울잇다를 Android 앱으로 만나보세요</h1>
        <p class="page-subtitle">
          스토어를 거치지 않고 이 페이지에서 APK 파일을 내려받아 설치할 수 있습니다.
          기존 웹페이지와 PWA도 계속 동일하게 이용할 수 있습니다.
        </p>
      </div>

      <a class="btn btn--primary" :href="apkUrl" download>
        Android APK 다운로드
      </a>

      <ol class="android-install-steps">
        <li>Android 휴대폰에서 위 버튼을 눌러 APK를 내려받습니다.</li>
        <li>브라우저가 요청하면 해당 브라우저의 ‘알 수 없는 앱 설치’를 허용합니다.</li>
        <li>다운로드한 파일을 열고 설치를 완료합니다.</li>
      </ol>

      <p class="helper-text">
        Android는 스토어 외부 앱 설치 시 보안 경고를 표시할 수 있습니다. 이 사이트에서 제공한 파일인지 확인한 후 설치하세요.
      </p>
    </section>
  </div>
</template>
