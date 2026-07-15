<script setup>
import { computed, nextTick, onMounted, ref, watch } from "vue";
import mascot from "../../assets/mascot.png";
import { sendChatMessage } from "../../api/chat";

const STORAGE_KEY = "seoul-itda-chat-history";
const isOpen = ref(false);
const input = ref("");
const isLoading = ref(false);
const messages = ref([]);
const initialMessage = { role: "assistant", content: "안녕하세요! 서울 관광지, 축제, 음식점과 커뮤니티 이야기를 데이터에 근거해 안내해드릴게요.", sources: [], metaLabel: "서울잇다 안내" };
const suggestions = ["이번 주 서울 축제 알려줘", "비 오는 날 갈 만한 곳은?", "가족과 가기 좋은 장소 추천해줘", "커뮤니티에서 인기 있는 이야기는?"];
const hasConversation = computed(() => messages.value.some((item) => item.role === "user"));

onMounted(() => {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    messages.value = Array.isArray(saved) && saved.length ? saved : [initialMessage];
  } catch {
    messages.value = [initialMessage];
  }
});

watch(messages, (value) => localStorage.setItem(STORAGE_KEY, JSON.stringify(value.slice(-30))), { deep: true });

async function scrollToBottom() {
  await nextTick();
  document.querySelector(".portal-chat__messages")?.scrollTo({ top: 999999, behavior: "smooth" });
}

async function sendMessage(text = input.value) {
  const question = text.trim();
  if (!question || isLoading.value) return;
  messages.value.push({ role: "user", content: question });
  input.value = "";
  isLoading.value = true;
  await scrollToBottom();
  try {
    const response = await sendChatMessage({ question });
    messages.value.push({
      role: "assistant",
      content: response?.answer || response?.message || "답변을 만들지 못했습니다. 잠시 후 다시 시도해주세요.",
      sources: Array.isArray(response?.sources) ? response.sources : [],
      metaLabel: response?.fallback ? "데이터 기반 안내" : "AI 데이터 안내",
    });
  } catch (error) {
    messages.value.push({ role: "assistant", content: error.message || "서버 응답을 받지 못했습니다.", sources: [], metaLabel: "연결 오류" });
  } finally {
    isLoading.value = false;
    scrollToBottom();
  }
}

function resetChat() {
  messages.value = [initialMessage];
}

function handleKeydown(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}
</script>

<template>
  <div class="portal-chat">
    <section v-if="isOpen" class="portal-chat__panel" aria-label="서울잇다 AI 안내">
      <header>
        <div class="portal-chat__identity"><img :src="mascot" alt="" /><span><strong>서울잇다 AI 안내</strong><small><i></i> 서울 데이터 연결됨</small></span></div>
        <div><button type="button" title="대화 초기화" @click="resetChat">↻</button><button type="button" title="닫기" @click="isOpen = false">×</button></div>
      </header>
      <div class="portal-chat__notice">제공된 서울 관광·축제·커뮤니티 데이터 안에서 답변합니다.</div>
      <div class="portal-chat__messages">
        <article v-for="(message,index) in messages" :key="index" :class="`portal-message portal-message--${message.role}`">
          <small v-if="message.metaLabel">{{ message.metaLabel }}</small>
          <p>{{ message.content }}</p>
          <div v-if="message.sources?.length"><span v-for="source in message.sources" :key="source">{{ source.replace(/^attraction:/, '장소 ').replace(/^post:/, '글 #') }}</span></div>
        </article>
        <article v-if="isLoading" class="portal-message portal-message--assistant portal-message--loading"><b></b><b></b><b></b></article>
      </div>
      <div v-if="!hasConversation" class="portal-chat__suggestions">
        <button v-for="suggestion in suggestions" :key="suggestion" type="button" @click="sendMessage(suggestion)">{{ suggestion }}</button>
      </div>
      <div class="portal-chat__composer">
        <textarea v-model="input" rows="2" placeholder="서울에 대해 무엇이 궁금하세요?" @keydown="handleKeydown"></textarea>
        <button type="button" :disabled="!input.trim() || isLoading" @click="sendMessage()">전송</button>
      </div>
    </section>
    <button class="portal-chat__toggle" type="button" @click="isOpen = !isOpen">
      <img :src="mascot" alt="" /><span><strong>AI 안내</strong><small>서울 정보 물어보기</small></span><b>{{ isOpen ? '×' : '＋' }}</b>
    </button>
  </div>
</template>
