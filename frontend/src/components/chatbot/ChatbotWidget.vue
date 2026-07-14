<script setup>
import { computed, nextTick, ref } from "vue";
import mascot from "../../assets/mascot.svg";
import { sendChatMessage } from "../../api/chat";

const isOpen = ref(false);
const input = ref("");
const isLoading = ref(false);
const messages = ref([
  {
    role: "assistant",
    content:
      "서울잇다 챗봇입니다. 서울 관광지, 축제, 맛집, 커뮤니티 글에 대해 질문해보세요.",
  },
]);

const suggestions = [
  "비 오는 날 서울 코스 추천해줘",
  "이번 달 서울 축제 알려줘",
  "이번 주말 열리는 축제 추천해줘",
  "서울 맛집 추천해줘",
];

const hasMessages = computed(() => messages.value.length > 1);

function togglePanel() {
  isOpen.value = !isOpen.value;
}

function addSuggestion(text) {
  input.value = text;
}

async function sendMessage() {
  const trimmed = input.value.trim();
  if (!trimmed || isLoading.value) {
    return;
  }

  messages.value.push({ role: "user", content: trimmed });
  input.value = "";
  isLoading.value = true;

  try {
    const response = await sendChatMessage({ message: trimmed });
    const content =
      response?.answer ||
      response?.message ||
      "답변을 생성하지 못했습니다. 잠시 후 다시 시도해주세요.";
    messages.value.push({ role: "assistant", content });
  } catch (error) {
    messages.value.push({
      role: "assistant",
      content: error.message || "챗봇 응답을 받지 못했습니다.",
    });
  } finally {
    isLoading.value = false;
    nextTick(() => {
      const container = document.querySelector(".chat-panel__messages");
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    });
  }
}

function handleKeydown(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

function resetChat() {
  messages.value = [
    {
      role: "assistant",
      content:
        "서울잇다 챗봇입니다. 서울 관광지, 축제, 맛집, 커뮤니티 글에 대해 질문해보세요.",
    },
  ];
}
</script>

<template>
  <div class="chatbot-widget">
    <button
      class="chatbot-toggle"
      type="button"
      @click="togglePanel"
      aria-label="챗봇 열기"
    >
      <img :src="mascot" alt="챗봇 마스코트" />
      <span>챗봇</span>
    </button>

    <div v-if="isOpen" class="chat-panel section-card">
      <div class="chat-panel__header">
        <div>
          <strong>서울잇다 챗봇</strong>
          <p>서울 정보와 커뮤니티 글을 바탕으로 답변해드려요.</p>
        </div>
        <div class="chat-panel__actions">
          <button class="icon-button" type="button" @click="resetChat">
            초기화
          </button>
          <button class="icon-button" type="button" @click="togglePanel">
            닫기
          </button>
        </div>
      </div>

      <div class="chat-panel__messages">
        <div
          v-for="(message, index) in messages"
          :key="`${message.role}-${index}`"
          :class="[
            'chat-bubble',
            message.role === 'user'
              ? 'chat-bubble--user'
              : 'chat-bubble--assistant',
          ]"
        >
          <p>{{ message.content }}</p>
        </div>
        <div v-if="isLoading" class="chat-bubble chat-bubble--assistant">
          <p>답변 생성 중...</p>
        </div>
      </div>

      <div v-if="!hasMessages" class="chat-suggestions">
        <button
          v-for="suggestion in suggestions"
          :key="suggestion"
          class="suggestion-chip"
          type="button"
          @click="addSuggestion(suggestion)"
        >
          {{ suggestion }}
        </button>
      </div>

      <div class="chat-panel__composer">
        <textarea
          v-model="input"
          class="textarea textarea--compact"
          rows="3"
          placeholder="질문을 입력하세요"
          @keydown="handleKeydown"
        />
        <button class="btn btn--primary" type="button" @click="sendMessage">
          전송
        </button>
      </div>
    </div>
  </div>
</template>
