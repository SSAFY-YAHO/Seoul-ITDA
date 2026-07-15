<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import mascot from "../assets/mascot.png";
import { fetchLocations } from "../api/locations";
import { fetchFestivals } from "../api/festivals";
import { parseFestivalDateRange } from "../utils/festivalDate";

const router = useRouter();
const query = ref("");
const locations = ref([]);
const festivals = ref([]);
const loading = ref(true);
const error = ref("");
const exploreMode = ref("theme");
const activeTheme = ref("전체");
const activeDistrict = ref("전체");

const themes = ["전체", "관광지", "문화", "쇼핑", "레포츠", "숙박"];

const categoryNames = {
  tourist: "관광지",
  culture: "문화",
  shopping: "쇼핑",
  leisure: "레포츠",
  hotel: "숙박",
  festival: "축제",
};

const districts = computed(() => [
  "전체",
  ...new Set(locations.value.map((item) => item.district).filter(Boolean)),
]);

const filteredLocations = computed(() => {
  const keyword = query.value.trim().toLowerCase();
  return locations.value
    .filter((item) => {
      const category = categoryNames[item.category] || item.category || "관광지";
      const themeMatched = activeTheme.value === "전체" || category === activeTheme.value;
      const districtMatched = activeDistrict.value === "전체" || item.district === activeDistrict.value;
      const searchText = [item.name, item.title, item.description, item.address, item.tags]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      const filterMatched = exploreMode.value === "theme" ? themeMatched : districtMatched;
      return filterMatched && (!keyword || searchText.includes(keyword));
    })
    .slice(0, 8);
});

const upcomingFestivals = computed(() => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return festivals.value
    .map((festival) => ({ festival, range: parseFestivalDateRange(festival) }))
    .filter(({ range }) => !range || range.end >= today)
    .sort((a, b) => (a.range?.start || today) - (b.range?.start || today))
    .slice(0, 3);
});

const galleryFestivals = computed(() =>
  festivals.value
    .filter((item) => item.imageUrl || item.image_url || item.mainImage)
    .slice(0, 6),
);

const overviewLocations = computed(() => locations.value.slice(0, 7));

function festivalImage(item) {
  return item.imageUrl || item.image_url || item.mainImage || "";
}

function selectOverviewLocation(location) {
  query.value = location.name || location.title || "";
  activeDistrict.value = location.district || "전체";
  exploreMode.value = "region";
  submitSearch();
}

function categoryLabel(item) {
  return categoryNames[item.category] || item.category || "서울 명소";
}

function festivalTitle(item) {
  return item.title || item.name || item.festivalName || "서울 축제";
}

function festivalDate(item) {
  const range = parseFestivalDateRange(item);
  if (!range) return "일정 준비 중";
  const options = { month: "short", day: "numeric" };
  return `${range.start.toLocaleDateString("ko-KR", options)} - ${range.end.toLocaleDateString("ko-KR", options)}`;
}

function submitSearch() {
  document.querySelector("#places")?.scrollIntoView({ behavior: "smooth" });
}

async function loadHomeData() {
  loading.value = true;
  error.value = "";
  try {
    const [locationData, festivalData] = await Promise.all([
      fetchLocations(),
      fetchFestivals().catch(() => []),
    ]);
    locations.value = Array.isArray(locationData) ? locationData : locationData?.items || [];
    festivals.value = Array.isArray(festivalData) ? festivalData : festivalData?.items || [];
  } catch (err) {
    error.value = err.message || "서울 정보를 불러오지 못했습니다.";
  } finally {
    loading.value = false;
  }
}

onMounted(loadHomeData);
</script>

<template>
  <div class="forest-home">
    <section class="forest-hero">
      <div class="forest-hero__sun" aria-hidden="true"></div>
      <div class="forest-hero__copy">
        <p class="forest-eyebrow">SEOUL LOCAL DISCOVERY</p>
        <h1>서울의 오늘을<br><em>가볍게 잇다</em></h1>
        <p class="forest-lead">
          공공데이터로 찾은 서울 명소부터 축제 일정, 여행자의 생생한 이야기까지
          한곳에서 둘러보세요.
        </p>
        <form class="forest-search" @submit.prevent="submitSearch">
          <span aria-hidden="true">⌕</span>
          <input v-model="query" type="search" placeholder="어디로 떠나볼까요? 장소나 테마를 검색해보세요" />
          <button type="submit">찾아보기</button>
        </form>
        <div class="forest-quick-links">
          <button type="button" @click="router.push('/festivals')">이번 달 축제</button>
          <button type="button" @click="router.push('/posts')">여행 이야기</button>
          <button type="button" @click="activeTheme = '문화'; submitSearch()">문화 산책</button>
        </div>
      </div>
      <div class="forest-hero__scene" aria-hidden="true">
        <span class="cloud cloud--one"></span>
        <span class="cloud cloud--two"></span>
        <div class="seoul-tower"><i></i></div>
        <div class="hill hill--back"></div>
        <div class="hill hill--front"></div>
        <span v-for="n in 9" :key="n" :class="`tree tree--${n}`"></span>
        <img :src="mascot" alt="" />
      </div>
      <div class="forest-wave" aria-hidden="true"></div>
    </section>

    <main class="forest-content">
      <section class="news-strip">
        <div class="news-strip__title">
          <span>새소식</span>
          <strong>서울의 이번 주</strong>
        </div>
        <article v-for="item in upcomingFestivals" :key="item.festival.id || festivalTitle(item.festival)">
          <small>{{ festivalDate(item.festival) }}</small>
          <strong>{{ festivalTitle(item.festival) }}</strong>
        </article>
        <button type="button" aria-label="축제 전체 보기" @click="router.push('/festivals')">＋</button>
      </section>

      <section id="places" class="discovery-section">
        <header class="forest-heading">
          <p>삶 속으로 들어온 서울</p>
          <h2>취향대로 발견하는<br><em>우리 동네 이야기</em></h2>
        </header>
        <div class="explore-switch" role="tablist" aria-label="탐색 기준">
          <button type="button" :class="{ active: exploreMode === 'region' }" @click="exploreMode = 'region'">지역</button>
          <button type="button" :class="{ active: exploreMode === 'theme' }" @click="exploreMode = 'theme'">테마</button>
        </div>
        <div v-if="exploreMode === 'theme'" class="theme-tabs" role="tablist" aria-label="장소 테마">
          <button
            v-for="theme in themes"
            :key="theme"
            type="button"
            :class="{ active: activeTheme === theme }"
            @click="activeTheme = theme"
          >
            {{ theme }}
          </button>
        </div>
        <div v-else class="theme-tabs district-tabs" role="tablist" aria-label="서울 지역">
          <button
            v-for="district in districts"
            :key="district"
            type="button"
            :class="{ active: activeDistrict === district }"
            @click="activeDistrict = district"
          >
            {{ district }}
          </button>
        </div>

        <div v-if="loading" class="forest-state">서울 곳곳의 이야기를 모으고 있어요…</div>
        <div v-else-if="error" class="forest-state forest-state--error">
          <strong>정보를 불러오지 못했습니다.</strong>
          <span>{{ error }}</span>
          <button type="button" @click="loadHomeData">다시 시도</button>
        </div>
        <div v-else-if="filteredLocations.length === 0" class="forest-state">
          검색 결과가 없습니다. 다른 검색어나 테마를 선택해보세요.
        </div>
        <div v-else class="place-gallery">
          <article v-for="(location, index) in filteredLocations" :key="location.id || location.name" class="place-tile">
            <div :class="`place-tile__art place-tile__art--${(index % 4) + 1}`">
              <span>{{ categoryLabel(location) }}</span>
              <i aria-hidden="true"></i>
            </div>
            <div class="place-tile__body">
              <small>{{ location.district || "서울" }}</small>
              <h3>{{ location.name || location.title || "이름 없는 장소" }}</h3>
              <p>{{ location.description || "서울에서 만나는 특별한 장소입니다." }}</p>
              <span>{{ location.address || "주소 정보 준비 중" }}</span>
            </div>
          </article>
        </div>
      </section>

      <section class="overview-section">
        <header class="forest-heading">
          <p>SEOUL AT A GLANCE</p>
          <h2>서울잇다<br><em>한눈에 보기</em></h2>
        </header>
        <div class="overview-board">
          <div class="river" aria-hidden="true"></div>
          <span class="overview-label">SEOUL</span>
          <button
            v-for="(location, index) in overviewLocations"
            :key="location.id || location.name"
            type="button"
            :class="`hotspot hotspot--${index + 1}`"
            @click="selectOverviewLocation(location)"
          >
            {{ location.name || location.title }} →
          </button>
        </div>
        <p class="overview-help">장소를 선택하면 해당 지역의 정보로 바로 이동합니다.</p>
      </section>

      <section v-if="galleryFestivals.length" class="gallery-section">
        <div class="gallery-title">
          <img :src="mascot" alt="" />
          <div><small>서울의 장면들</small><h2>축제 갤러리</h2></div>
          <button type="button" @click="router.push('/festivals')">전체 보기 →</button>
        </div>
        <div class="festival-gallery">
          <article v-for="festival in galleryFestivals" :key="festival.id || festivalTitle(festival)">
            <img :src="festivalImage(festival)" :alt="festivalTitle(festival)" loading="lazy" />
            <div><small>{{ festivalDate(festival) }}</small><strong>{{ festivalTitle(festival) }}</strong></div>
          </article>
        </div>
      </section>

      <section class="community-banner">
        <div class="community-banner__art" aria-hidden="true">
          <span class="mini-tree"></span><span class="mini-tree mini-tree--two"></span>
          <img :src="mascot" alt="" />
        </div>
        <div>
          <p>LOCAL COMMUNITY</p>
          <h2>여행자의 서울은<br>조금 더 다정하니까</h2>
          <span>궁금한 것을 묻고, 발견한 장소와 경험을 익명으로 나눠보세요.</span>
        </div>
        <button type="button" @click="router.push('/posts')">커뮤니티 둘러보기 →</button>
      </section>
    </main>
  </div>
</template>

<style scoped>
.forest-home { overflow: hidden; background: #fbfbef; color: #294437; }
.forest-hero { position: relative; min-height: 650px; padding: 90px max(7vw, 24px) 150px; background: linear-gradient(180deg, #dff3e2 0%, #eef7d9 70%, #fbfbef 100%); }
.forest-hero__copy { position: relative; z-index: 5; width: min(620px, 52vw); }
.forest-eyebrow, .forest-heading p, .community-banner p { margin: 0 0 12px; color: #4d9b4b; font-weight: 900; font-size: 13px; letter-spacing: .18em; }
.forest-hero h1 { margin: 0; font-size: clamp(48px, 6vw, 86px); line-height: .98; letter-spacing: -.065em; }
.forest-hero h1 em, .forest-heading em { color: #2c9a4b; font-style: normal; }
.forest-lead { max-width: 570px; margin: 26px 0; color: #557064; font-size: 17px; line-height: 1.75; }
.forest-search { display: flex; align-items: center; gap: 12px; max-width: 620px; padding: 9px 10px 9px 20px; border: 3px solid #42664d; border-radius: 999px; background: white; box-shadow: 0 15px 0 rgba(65, 101, 76, .1); }
.forest-search > span { color: #369d4c; font-size: 30px; line-height: 1; }
.forest-search input { min-width: 0; flex: 1; border: 0; outline: 0; background: transparent; color: #294437; font: inherit; }
.forest-search button, .community-banner > button { padding: 14px 22px; border: 0; border-radius: 999px; background: #35a74e; color: white; font-weight: 900; }
.forest-quick-links { display: flex; gap: 10px; margin-top: 22px; flex-wrap: wrap; }
.forest-quick-links button, .theme-tabs button { padding: 9px 17px; border: 1px solid rgba(45, 104, 60, .18); border-radius: 999px; background: rgba(255,255,255,.7); color: #496455; font-weight: 800; }
.forest-hero__sun { position: absolute; top: 58px; right: 8%; width: 125px; height: 125px; border-radius: 50%; background: #ffe36e; opacity: .8; }
.forest-hero__scene { position: absolute; right: 0; bottom: 60px; width: 53%; height: 88%; }
.hill { position: absolute; bottom: 0; border-radius: 55% 45% 0 0 / 70% 70% 0 0; }
.hill--back { right: -8%; width: 100%; height: 58%; background: #9bd47f; transform: rotate(-3deg); }
.hill--front { right: -22%; width: 105%; height: 42%; background: #58b769; transform: rotate(4deg); }
.cloud { position: absolute; width: 95px; height: 30px; border-radius: 40px; background: rgba(255,255,255,.8); }
.cloud::before, .cloud::after { content: ""; position: absolute; bottom: 0; border-radius: 50%; background: inherit; }
.cloud::before { left: 18px; width: 44px; height: 44px; }.cloud::after { right: 12px; width: 32px; height: 32px; }
.cloud--one { top: 90px; left: 4%; }.cloud--two { top: 170px; right: 10%; transform: scale(.75); }
.seoul-tower { position: absolute; z-index: 2; right: 30%; bottom: 38%; width: 23px; height: 210px; background: #f7f0d5; border: 7px solid #315844; border-radius: 10px 10px 0 0; }
.seoul-tower::before { content: ""; position: absolute; left: 50%; top: -90px; width: 6px; height: 90px; background: #315844; transform: translateX(-50%); }
.seoul-tower i { position: absolute; left: 50%; top: 30px; width: 78px; height: 30px; border: 7px solid #315844; border-radius: 50%; background: #f4a15e; transform: translateX(-50%); }
.tree { position: absolute; z-index: 3; bottom: 12%; width: 34px; height: 90px; border-radius: 50% 50% 20% 20%; background: #267e50; border: 5px solid #315844; transform-origin: bottom; }
.tree::after { content: ""; position: absolute; left: 50%; bottom: -20px; width: 7px; height: 25px; background: #765c3b; transform: translateX(-50%); }
.tree--1 { left: 5%; transform: scale(.8) rotate(-6deg); }.tree--2 { left: 14%; bottom: 6%; background:#75bd61; }.tree--3 { left: 28%; transform: scale(1.2); }.tree--4 { right: 6%; bottom: 20%; }.tree--5 { right: 16%; background:#8acb62; transform:scale(.75); }.tree--6 { right: 42%; bottom: 3%; }.tree--7 { left: 43%; bottom: 20%; transform:scale(.65); }.tree--8 { right: 2%; bottom: 2%; background:#75bd61; }.tree--9 { left: 2%; bottom: 30%; transform:scale(.6); }
.forest-hero__scene img { position: absolute; z-index: 5; right: 10%; bottom: 5%; width: clamp(120px, 15vw, 210px); filter: drop-shadow(0 14px 10px rgba(38,85,54,.2)); }
.forest-wave { position: absolute; z-index: 4; left: -5%; right: -5%; bottom: -56px; height: 130px; border-radius: 50% 50% 0 0; background: #fbfbef; }
.forest-content { width: min(1320px, calc(100% - 48px)); margin: 0 auto; padding: 10px 0 80px; }
.news-strip { position: relative; z-index: 6; display: grid; grid-template-columns: 190px repeat(3, 1fr) 46px; gap: 24px; align-items: center; min-height: 126px; padding: 20px 28px; border: 1px solid #dbe8d2; border-radius: 28px; background: white; box-shadow: 0 16px 45px rgba(47,91,57,.08); }
.news-strip__title span { display:block; color:#2b9c4b; font-weight:900; }.news-strip__title strong { font-size:20px; }
.news-strip article { min-width:0; padding-left:22px; border-left:1px solid #e4ebdf; }.news-strip article small { display:block; color:#7f9787; }.news-strip article strong { display:block; margin-top:5px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
.news-strip > button { width:42px; height:42px; border:1px solid #dce7d7; border-radius:50%; background:#f7fbf4; color:#3b8850; font-size:21px; }
.discovery-section { padding: 110px 0 70px; }
.forest-heading { text-align:center; }.forest-heading h2 { margin:0; font-size:clamp(34px,4vw,58px); line-height:1.12; letter-spacing:-.05em; }
.explore-switch { display:grid; grid-template-columns:1fr 1fr; width:min(480px,100%); margin:28px auto 12px; padding:5px; border:1px solid #bcd8b9; border-radius:999px; background:white; }
.explore-switch button { padding:10px; border:0; border-radius:999px; background:transparent; color:#6d8374; font-weight:900; }
.explore-switch button.active { background:#36a44e; color:white; box-shadow:0 6px 15px rgba(42,139,65,.2); }
.theme-tabs { display:flex; justify-content:center; gap:8px; margin:30px 0 38px; flex-wrap:wrap; }.theme-tabs button.active { border-color:#359c4c; background:#359c4c; color:white; }
.district-tabs { margin-top:12px; }
.place-gallery { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:22px; }
.place-tile { overflow:hidden; border:1px solid #dfe8da; border-radius:26px; background:white; box-shadow:0 14px 30px rgba(54,91,61,.07); transition:.25s ease; }.place-tile:hover { transform:translateY(-7px); box-shadow:0 20px 40px rgba(54,91,61,.13); }
.place-tile__art { position:relative; height:150px; overflow:hidden; padding:18px; background:#bce1b3; }.place-tile__art span { position:relative; z-index:3; padding:6px 11px; border-radius:999px; background:rgba(255,255,255,.85); color:#327746; font-size:12px; font-weight:900; }.place-tile__art i { position:absolute; right:-10%; bottom:-45%; width:85%; height:130%; border-radius:50% 50% 0 0; background:#65b96d; transform:rotate(-12deg); }.place-tile__art::after { content:""; position:absolute; left:18%; bottom:0; width:56px; height:92px; border-radius:28px 28px 0 0; background:#fff6d7; border:5px solid #3e6a50; }
.place-tile__art--2 { background:#c8e9e6; }.place-tile__art--2 i { background:#6ebec1; }.place-tile__art--3 { background:#f4df9e; }.place-tile__art--3 i { background:#efad5c; }.place-tile__art--4 { background:#cbd9ef; }.place-tile__art--4 i { background:#819fc9; }
.place-tile__body { padding:20px; }.place-tile__body small { color:#399553; font-weight:900; }.place-tile__body h3 { margin:7px 0 9px; font-size:19px; }.place-tile__body p { display:-webkit-box; min-height:44px; margin:0 0 13px; overflow:hidden; color:#64786c; font-size:14px; -webkit-box-orient:vertical; -webkit-line-clamp:2; }.place-tile__body > span { display:block; overflow:hidden; color:#8a998f; font-size:12px; white-space:nowrap; text-overflow:ellipsis; }
.forest-state { display:grid; place-items:center; gap:10px; min-height:220px; border:1px dashed #bad3b8; border-radius:28px; background:rgba(255,255,255,.65); color:#68806f; }.forest-state--error button { padding:9px 17px; border:0; border-radius:999px; background:#399a4f; color:white; font-weight:800; }
.overview-section { margin:40px calc(50% - 50vw) 0; padding:90px max(7vw,24px) 105px; background:linear-gradient(180deg,#dff5f5,#eff9e5); }
.overview-board { position:relative; width:min(1000px,100%); height:500px; margin:38px auto 15px; overflow:hidden; border:8px solid white; border-radius:36px; background:linear-gradient(145deg,#cce2b4,#eef1c5); box-shadow:0 22px 45px rgba(47,100,75,.16); }
.overview-board::before,.overview-board::after { content:""; position:absolute; width:70%; height:120%; border:22px solid rgba(255,255,255,.5); border-radius:45%; transform:rotate(18deg); }
.overview-board::before { left:-18%; top:-55%; }.overview-board::after { right:-22%; bottom:-70%; }
.river { position:absolute; z-index:1; left:-10%; top:45%; width:120%; height:95px; background:#8ed7dc; transform:rotate(-8deg); box-shadow:inset 0 12px rgba(255,255,255,.25); }
.overview-label { position:absolute; z-index:2; left:50%; top:50%; color:rgba(42,112,75,.14); font-size:100px; font-weight:1000; transform:translate(-50%,-50%) rotate(-8deg); }
.hotspot { position:absolute; z-index:3; padding:10px 17px; border:3px solid white; border-radius:999px; background:#32af61; color:white; font-weight:900; box-shadow:0 8px 16px rgba(33,106,65,.24); transition:.2s ease; }.hotspot:hover { transform:translateY(-4px) scale(1.03); }
.hotspot--1 { left:8%; top:17%; }.hotspot--2 { left:39%; top:12%; }.hotspot--3 { right:8%; top:26%; }.hotspot--4 { left:17%; bottom:21%; }.hotspot--5 { left:46%; bottom:12%; }.hotspot--6 { right:7%; bottom:25%; }.hotspot--7 { left:42%; top:47%; }
.overview-help { text-align:center; color:#688075; }
.gallery-section { display:grid; grid-template-columns:260px minmax(0,1fr); gap:25px; margin:0 calc(50% - 50vw); padding:75px max(7vw,24px); background:#eef8ef; }
.gallery-title { display:grid; align-content:center; justify-items:start; }.gallery-title img { width:100px; }.gallery-title small { color:#3c9a51; font-weight:900; }.gallery-title h2 { margin:3px 0 18px; font-size:34px; }.gallery-title button { padding:9px 14px; border:1px solid #bdd8bd; border-radius:999px; background:white; color:#367a48; font-weight:800; }
.festival-gallery { display:flex; gap:16px; overflow-x:auto; padding:8px 4px 18px; scroll-snap-type:x mandatory; }.festival-gallery article { position:relative; flex:0 0 230px; height:280px; overflow:hidden; border-radius:24px; background:#d5e7d3; scroll-snap-align:start; }.festival-gallery img { width:100%; height:100%; object-fit:cover; transition:.3s ease; }.festival-gallery article:hover img { transform:scale(1.05); }.festival-gallery article div { position:absolute; inset:auto 0 0; display:grid; padding:38px 16px 16px; background:linear-gradient(transparent,rgba(21,49,33,.82)); color:white; }.festival-gallery small { opacity:.8; }.festival-gallery strong { overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
.community-banner { position:relative; display:grid; grid-template-columns:260px 1fr auto; align-items:center; gap:42px; min-height:280px; padding:40px 55px; overflow:hidden; border-radius:42px; background:linear-gradient(120deg,#cdeedc,#eaf5ce); }.community-banner h2 { margin:0 0 12px; font-size:clamp(30px,3.5vw,48px); line-height:1.08; }.community-banner > div > span { color:#587266; }.community-banner__art { position:relative; align-self:stretch; }.community-banner__art img { position:absolute; z-index:2; left:55px; bottom:-45px; width:150px; }.mini-tree { position:absolute; left:8px; bottom:-40px; width:100px; height:200px; border-radius:50% 50% 16px 16px; background:#4fa665; transform:rotate(-6deg); }.mini-tree--two { left:145px; bottom:-60px; background:#91c96e; transform:scale(.7) rotate(8deg); }
@media (max-width: 960px) { .forest-hero { min-height:760px; }.forest-hero__copy { width:100%; }.forest-hero__scene { width:75%; height:54%; opacity:.9; }.news-strip { grid-template-columns:1fr 1fr; }.news-strip__title { grid-column:1/-1; }.news-strip > button { display:none; }.place-gallery { grid-template-columns:repeat(2,1fr); }.gallery-section { grid-template-columns:1fr; }.gallery-title { grid-template-columns:auto 1fr auto; align-items:center; gap:15px; }.gallery-title h2 { margin:0; }.community-banner { grid-template-columns:180px 1fr; }.community-banner > button { grid-column:2; justify-self:start; }.community-banner__art img { left:20px; } }
@media (max-width: 640px) { .forest-hero { min-height:700px; padding:60px 20px 160px; }.forest-hero h1 { font-size:48px; }.forest-lead { font-size:15px; }.forest-search { padding-left:14px; }.forest-search button { padding:12px 15px; }.forest-hero__scene { width:100%; height:43%; bottom:65px; }.forest-hero__scene img { width:115px; }.forest-content { width:min(100% - 28px,1320px); }.news-strip { grid-template-columns:1fr; gap:14px; padding:22px; }.news-strip article { padding:12px 0 0; border-left:0; border-top:1px solid #e4ebdf; }.discovery-section { padding-top:75px; }.place-gallery { grid-template-columns:1fr; }.overview-board { height:440px; }.hotspot { max-width:145px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; font-size:12px; }.hotspot--3,.hotspot--6 { right:2%; }.gallery-title { grid-template-columns:auto 1fr; }.gallery-title button { grid-column:1/-1; }.community-banner { grid-template-columns:1fr; padding:30px; }.community-banner__art { display:none; }.community-banner > button { grid-column:auto; }.theme-tabs { justify-content:flex-start; overflow-x:auto; flex-wrap:nowrap; padding-bottom:5px; }.theme-tabs button { flex:0 0 auto; } }
</style>
