# Android APK 빌드 및 웹 배포

현재 배포 APK 버전은 `1.2.2`(`versionCode 5`)이며 게시글 댓글·대댓글 작성/조회, 댓글별 좋아요, 서울잇다 공식 앱 아이콘과 최신 다운로드 화면을 포함한다.

서울잇다 Android 앱은 기존 Vue 웹앱을 Capacitor WebView에서 실행합니다. 웹과 PWA 배포는 기존
Netlify 설정을 그대로 사용하고, Android 프로젝트는 `frontend/android/`에서 별도로 관리합니다.

## 준비물

- Android Studio와 Android SDK 36
- JDK 21
- Node.js 및 npm
- HTTPS로 배포된 FastAPI API 주소

Render의 `CORS_ORIGINS`에는 웹 배포 주소와 Capacitor 기본 출처인 `https://localhost`를 모두
등록합니다. 여러 주소는 쉼표로 구분합니다.

## APK 빌드

루트 `.env.android` 파일을 만들고 다음 값을 설정합니다. 실제 비밀키는 커밋하지 않습니다.

```dotenv
VITE_API_BASE_URL=https://your-render-service.onrender.com
VITE_CLOUDINARY_CLOUD_NAME=your_cloud_name
VITE_CLOUDINARY_UPLOAD_PRESET=your_unsigned_upload_preset
```

이후 다음 명령을 실행합니다.

```powershell
cd frontend
npm.cmd run android:apk
```

개발용 APK는 `frontend/android/app/build/outputs/apk/debug/app-debug.apk`에 생성됩니다. 팀 내부 또는
제한된 사용자에게 직접 배포할 때 사용할 수 있습니다. 장기 배포용 파일은 Android Studio에서
별도 서명 키로 release APK를 생성하고, 키 파일과 비밀번호는 저장소 밖에 보관합니다.

## 웹 다운로드 연결

완성된 APK를 `frontend/public/downloads/seoul-itda.apk`에 둔 뒤 Netlify 웹을 다시 배포합니다.
Netlify가 이 파일을 프론트 정적 자산으로 함께 배포하며 `/download` 페이지의 버튼은 항상
`/downloads/seoul-itda.apk`를 가리킵니다. 별도 APK 호스팅 URL이나 환경변수는 필요하지 않습니다.

Android 모드 빌드는 웹 배포용 APK가 앱 내부에 다시 포함되지 않도록 `dist/downloads`를 자동으로
제외합니다. 일반 웹 빌드는 해당 폴더를 유지하므로 Netlify 다운로드에는 영향이 없습니다.

## 업데이트

코드를 변경한 뒤 `npm.cmd run android:sync`를 실행하면 최신 웹 빌드가 Android 프로젝트에
반영됩니다. 사용자가 새 버전을 설치할 수 있도록 Android의 `versionCode`와 `versionName`을 올리고
동일한 서명 키로 APK를 다시 서명해야 합니다.
