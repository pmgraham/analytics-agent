<template>
  <div class="chat-container">
    <div class="messages">
      <div v-for="(message, index) in messages" :key="index" :class="['message', message.sender]">
        <div v-html="renderMarkdown(message.text)"></div>
      </div>
      <div v-if="isLoading" class="message bot loading">
        {{ currentStatus }}
      </div>
    </div>
    <div class="input-area">
      <input
        v-model="newMessage"
        @keyup.enter="sendMessage"
        placeholder="Type your message..."
        :disabled="isLoading"
      />
      <button @click="sendMessage" :disabled="isLoading">Send</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { sendMessageToApi, createSession } from '../api';
import { marked } from 'marked';
import hljs from 'highlight.js';
import javascript from 'highlight.js/lib/languages/javascript';
import python from 'highlight.js/lib/languages/python';
import sql from 'highlight.js/lib/languages/sql';

hljs.registerLanguage('javascript', javascript);
hljs.registerLanguage('python', python);
hljs.registerLanguage('sql', sql);
import 'highlight.js/styles/atom-one-dark.css'; // Using atom-one-dark theme

marked.setOptions({
  highlight: function(code, lang) {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext';
    console.log('Language used for highlighting:', language);
    return hljs.highlight(code, { language }).value;
  },
  langPrefix: 'hljs language-', // highlight.js css expects this
});

const messages = ref([]);
const newMessage = ref('');
const isLoading = ref(false);
const currentStatus = ref('Typing...'); // New ref for agent status
const currentSessionId = ref(null);
const appName = "agent"; // Define appName
const userId = "default-user"; // Define userId

const renderMarkdown = (text) => {
  return marked.parse(text);
};

onMounted(async () => {
  try {
    currentSessionId.value = await createSession(appName, userId);
    console.log('Session created:', currentSessionId.value);
  } catch (error) {
    console.error('Error creating session:', error);
    messages.value.push({ text: 'Error: Could not create session.', sender: 'bot' });
  }
});

const sendMessage = async () => {
  if (newMessage.value.trim() === '') return;
  if (!currentSessionId.value) {
    messages.value.push({ text: 'Error: Session not established.', sender: 'bot' });
    return;
  }

  messages.value.push({ text: newMessage.value, sender: 'user' });
  const userMessage = newMessage.value;
  newMessage.value = '';

  isLoading.value = true;
  currentStatus.value = 'Typing...'; // Initial status
  let fullResponse = '';

  try {
    for await (const chunk of sendMessageToApi(userMessage, appName, userId, currentSessionId.value)) {
      if (chunk.type === 'status') {
        currentStatus.value = chunk.message;
      } else if (chunk.type === 'text') {
        fullResponse += chunk.content;
        // Optionally update the last message in real-time if needed
        // For now, we'll just accumulate and add once at the end
      }
    }
    messages.value.push({ text: fullResponse, sender: 'bot' });
  } catch (error) {
    console.error('Error sending message:', error);
    messages.value.push({ text: 'Error: Could not get a response.', sender: 'bot' });
  } finally {
    isLoading.value = false;
    currentStatus.value = ''; // Clear status after response
  }
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 1000px; /* Increased max-width */
  margin: 0 auto;
  border: 1px solid #ccc;
  border-radius: 8px;
  overflow: hidden;
}

.messages {
  flex-grow: 1;
  padding: 10px;
  overflow-y: auto;
  background-color: #f9f9f9;
}

.message {
  margin-bottom: 8px;
  padding: 8px 12px;
  border-radius: 15px;
  max-width: 90%; /* Increased max-width for messages */
  word-wrap: break-word;
}

.message.user {
  align-self: flex-end;
  background-color: #007bff;
  color: white;
  margin-left: auto;
}

.message.bot {
  align-self: flex-start;
  background-color: #e2e2e2;
  color: #333;
  margin-right: auto;
}

.input-area {
  display: flex;
  padding: 10px;
  border-top: 1px solid #ccc;
  background-color: #fff;
}

.input-area input {
  flex-grow: 1;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 20px;
  margin-right: 10px;
  outline: none;
}

.input-area button {
  padding: 10px 20px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.message.bot.loading {
  background-color: #f0f0f0;
  color: #666;
  font-style: italic;
}

/* Styles for markdown rendering */
.message div :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
}

.message div :deep(th), .message div :deep(td) {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.message div :deep(th) {
  background-color: #f2f2f2;
}

.message div :deep(pre) {
  background-color: #2d2d2d;
  color: #f8f8f2;
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
  white-space: pre-wrap; /* Ensures long lines wrap */
  word-wrap: break-word; /* Ensures long words break */
}

.message div :deep(code) {
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Andale Mono', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
  line-height: 1.4; /* Improve readability for multi-line code */
}

.message div :deep(pre) code {
  display: block;
  padding: 0; /* Remove padding from inner code to avoid double padding */
  background-color: transparent; /* Ensure background is from pre */
  color: inherit; /* Inherit color from pre */
}

.message div :deep(p) {
  margin-top: 0; /* Remove top margin for paragraphs in messages */
  margin-bottom: 0.5em;
}

.message div :deep(ul),
.message div :deep(ol) {
  margin-left: 20px;
  padding-left: 0;
}

.message div :deep(li) {
  margin-bottom: 5px;
}

.message div :deep(a) {
  color: #007bff;
  text-decoration: underline;
}

.message div :deep(strong) {
  font-weight: bold;
}

.message div :deep(em) {
  font-style: italic;
}

.message div :deep(blockquote) {
  border-left: 4px solid #ccc;
  padding-left: 10px;
  color: #666;
  margin: 10px 0;
}

.message div :deep(h1),
.message div :deep(h2),
.message div :deep(h3),
.message div :deep(h4),
.message div :deep(h5),
.message div :deep(h6) {
  margin-top: 1em;
  margin-bottom: 0.5em;
  font-weight: bold;
}

.message div :deep(hr) {
  border: 0;
  border-top: 1px solid #eee;
  margin: 20px 0;
}
</style>
