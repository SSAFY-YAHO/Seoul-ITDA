<script setup>
import { computed, nextTick, onMounted, ref, watch } from "vue";
import brandMark from "../../assets/mascot.png";
import { sendChatMessage } from "../../api/chat";

const STORAGE_KEY = "seoul-itda-chat-messages";
const MAX_STORED_MESSAGES = 30;
const MAX_HISTORY_MESSAGE_LENGTH = 1000;
const INITIAL_MESSAGE = {
  role: "assistant",
  content: "안녕하세요! 편하게 대화해도 좋아요. 서울 장소를 찾을 때는 내부 데이터를 먼저 살펴보고, 없으면 웹에서 찾아드릴게요.",
  sources: [],
  metaLabel: "AI 대화",
};

const isOpen = ref(false);
const input = ref("");
const isLoading = ref(false);
const messages = ref([{ ...INITIAL_MESSAGE }]);
const messageListRef = ref(null);

const suggestions = [
  "안녕! 오늘 하루는 어땠어?",
  "이번 주 서울 축제 알려줘",
  "비 오는 날 갈 만한 곳은?",
  "가족과 가기 좋은 장소 추천해줘",
];

const hasConversation = computed(() => messages.value.length > 1);
const canSend = computed(() => input.value.trim().length > 0 && !isLoading.value);
const connectionLabel = computed(() => isLoading.value ? "답변 생성 중" : "대화 준비됨");

const MODE_LABELS = {
  conversation: "AI 대화",
  database: "서울잇다 데이터",
  web: "웹 검색",
};

function togglePanel() {
  isOpen.value = !isOpen.value;
  if (isOpen.value) scrollToBottom();
}

function closePanel() {
  isOpen.value = false;
}

function scrollToBottom() {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight;
    }
  });
}

function restoreMessages() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    if (Array.isArray(saved) && saved.length > 0) {
      messages.value = saved
        .filter((message) => message?.role && typeof message?.content === "string")
        .slice(-MAX_STORED_MESSAGES);
    }
  } catch (_error) {
    localStorage.removeItem(STORAGE_KEY);
  }
}

function persistMessages() {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(messages.value.slice(-MAX_STORED_MESSAGES)),
    );
  } catch (_error) {
    // 저장 공간을 사용할 수 없어도 현재 대화는 계속 동작한다.
  }
}

async function sendMessage(question = input.value) {
  const trimmed = String(question || "").trim();
  if (!trimmed || isLoading.value) return;

  const history = messages.value
    .filter((message) => ["user", "assistant"].includes(message?.role) && message?.content)
    .slice(-10)
    .map((message) => ({
      role: message.role,
      content: String(message.content).slice(0, MAX_HISTORY_MESSAGE_LENGTH),
    }));

  messages.value.push({ role: "user", content: trimmed, sources: [] });
  input.value = "";
  isLoading.value = true;
  scrollToBottom();

  try {
    const response = await sendChatMessage({ question: trimmed, history });
    const content = response?.answer || response?.message
      || "답변을 생성하지 못했습니다. 잠시 후 다시 시도해주세요.";
    const sources = Array.isArray(response?.sources)
      ? response.sources.map(normalizeSource).filter(Boolean)
      : [];
    messages.value.push({
      role: "assistant",
      content,
      sources,
      metaLabel: response?.fallback ? "연결 안내" : MODE_LABELS[response?.mode] || "AI 대화",
    });
  } catch (_error) {
    messages.value.push({
      role: "assistant",
      content: "답변을 불러오지 못했습니다. 잠시 후 같은 질문을 다시 보내주세요.",
      sources: [],
      metaLabel: "연결 오류",
    });
  } finally {
    isLoading.value = false;
    scrollToBottom();
  }
}

function handleKeydown(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    if (canSend.value) sendMessage();
  }
}

function resetChat() {
  messages.value = [{ ...INITIAL_MESSAGE }];
  input.value = "";
  localStorage.removeItem(STORAGE_KEY);
  scrollToBottom();
}

function formatSource(source) {
  if (!source || typeof source !== "object") return "";
  const prefix = {
    attraction: "장소 · ",
    post: "커뮤니티 · ",
    web: "웹 · ",
  }[source.type] || "출처 · ";
  return `${prefix}${source.title || source.url || "출처"}`;
}

function normalizeSource(source) {
  if (source && typeof source === "object") {
    return {
      type: source.type || "web",
      title: source.title || source.url || "출처",
      url: source.url || "",
    };
  }

  if (typeof source === "string") {
    const isPost = source.startsWith("post:");
    return {
      type: isPost ? "post" : "attraction",
      title: source.replace(/^(attraction|post):/, ""),
      url: "",
    };
  }

  return null;
}

function sourceKey(source, index) {
  return `${source.type}-${source.url || source.title}-${index}`;
}

function sourceTarget(source) {
  return source.url?.startsWith("/") ? undefined : "_blank";
}

onMounted(() => {
  restoreMessages();
  scrollToBottom();
});

watch(messages, () => {
  persistMessages();
  scrollToBottom();
}, { deep: true });
</script>

<template>
  <div class="chatbot-widget" :class="{ 'chatbot-widget--open': isOpen }">
    <div v-if="isOpen" class="chat-panel" role="dialog" aria-label="서울잇다 AI 안내">
      <header class="chat-panel__header">
        <div class="chat-panel__identity">
          <span class="chat-panel__mascot"><img :src="brandMark" alt="" /></span>
          <div>
            <strong>서울잇다 AI 안내</strong>
            <span class="chat-panel__status"><i></i>{{ connectionLabel }}</span>
          </div>
        </div>
        <div class="chat-panel__actions">
          <button class="chat-action-button" type="button" @click="resetChat" aria-label="대화 초기화">↻</button>
          <button class="chat-action-button" type="button" @click="closePanel" aria-label="챗봇 닫기">×</button>
        </div>
      </header>

      <p class="chat-panel__notice">일반 대화와 서울 장소 탐색을 도와드려요. 장소는 내부 데이터부터 확인합니다.</p>

      <div ref="messageListRef" class="chat-panel__messages" aria-live="polite">
        <article
          v-for="(message, index) in messages"
          :key="`${message.role}-${index}`"
          :class="['chat-message', `chat-message--${message.role}`]"
        >
          <span class="chat-message__role">{{ message.role === 'user' ? '나' : '서울잇다' }}</span>
          <div class="chat-bubble">
            <span v-if="message.metaLabel" class="chat-bubble__label">{{ message.metaLabel }}</span>
            <p>{{ message.content }}</p>
            <div v-if="message.sources?.length" class="chat-bubble__sources">
              <template v-for="(source, sourceIndex) in message.sources" :key="sourceKey(source, sourceIndex)">
                <a
                  v-if="source.url"
                  class="source-chip source-chip--link"
                  :href="source.url"
                  :target="sourceTarget(source)"
                  :rel="sourceTarget(source) ? 'noopener noreferrer' : undefined"
                >
                  {{ formatSource(source) }}
                </a>
                <span v-else class="source-chip">{{ formatSource(source) }}</span>
              </template>
            </div>
          </div>
        </article>

        <article v-if="isLoading" class="chat-message chat-message--assistant">
          <span class="chat-message__role">서울잇다</span>
          <div class="chat-bubble chat-loading" aria-label="답변 생성 중">
            <i></i><i></i><i></i>
          </div>
        </article>
      </div>

      <div v-if="!hasConversation" class="chat-suggestions">
        <span>이런 질문은 어떠세요?</span>
        <button
          v-for="suggestion in suggestions"
          :key="suggestion"
          class="suggestion-chip"
          type="button"
          :disabled="isLoading"
          @click="sendMessage(suggestion)"
        >
          {{ suggestion }}
        </button>
      </div>

      <div class="chat-panel__composer">
        <textarea
          v-model="input"
          rows="2"
          maxlength="500"
          placeholder="편하게 대화하거나 서울 장소를 물어보세요"
          aria-label="질문 입력"
          :disabled="isLoading"
          @keydown="handleKeydown"
        />
        <button class="chat-send-button" type="button" :disabled="!canSend" @click="sendMessage()">
          전송
        </button>
      </div>
    </div>

    <button
      v-else
      class="chatbot-toggle"
      type="button"
      @click="togglePanel"
      aria-label="서울잇다 AI 대화 열기"
    >
      <span class="chatbot-toggle__mascot"><img :src="brandMark" alt="서울잇다 해치" /></span>
      <span class="chatbot-toggle__copy"><span>서울 정보 물어보기</span></span>
      <span class="chatbot-toggle__arrow" aria-hidden="true">›</span>
    </button>
  </div>
</template>
