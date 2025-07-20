<template>
  <div class="combined-container">
    <div class="editor-panel">
      <div class="editor-wrapper">
        <div class="line-numbers" ref="lineNumbersRef">
          <span v-for="n in lineNumbers" :key="n">{{ n }}</span>
        </div>
        <textarea
          ref="editorRef"
          v-model="editorContent"
          placeholder="Write your code or text here..."
          @input="updateLineNumbers"
          @scroll="handleScroll"
        ></textarea>
      </div>
      <button @click="insertIntoChat" class="insert-button">Insert into Chat</button>
    </div>

    <div class="chat-panel">
      <div class="messages" ref="messagesContainer">
        <div v-for="(message, index) in messages" :key="index" :class="['message', message.sender]">
          <div v-html="renderMarkdown(message.text)"></div>
        </div>
        <div v-if="isLoading" class="message bot loading">
          {{ currentStatus }}
        </div>
        <div v-if="isLoading && currentStreamingMessage" class="message bot streaming-message">
          <div v-html="renderMarkdown(currentStreamingMessage)"></div>
        </div>
      </div>
      <div class="input-area">
        <input
          v-model="newMessage"
          @keyup.enter="sendMessage"
          placeholder="Type your message..."
          :disabled="isLoading"
        />
        <button @click="sendMessage" :disabled="isLoading" class="insert-button">Send</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, watch } from 'vue';
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
const currentStreamingMessage = ref(''); // New ref for streaming message
const currentSessionId = ref(null);
const appName = "agent"; // Define appName
const userId = "default-user"; // Define userId

// Text Editor Refs and Logic
const editorContent = ref('');
const editorRef = ref(null); // Ref for the textarea element
const lineNumbersRef = ref(null); // Ref for the line numbers div

const lineNumbers = computed(() => {
  const lines = editorContent.value.split('\n');
  return Array.from({ length: lines.length }, (_, i) => i + 1);
});

const updateLineNumbers = () => {
  nextTick(() => {
    handleScroll();
  });
};

const handleScroll = () => {
  if (editorRef.value && lineNumbersRef.value) {
    lineNumbersRef.value.scrollTop = editorRef.value.scrollTop;
  }
};

watch(editorContent, () => {
  updateLineNumbers();
});

const insertIntoChat = () => {
  const textarea = editorRef.value;
  let contentToInsert = editorContent.value;

  if (textarea && textarea.selectionStart !== textarea.selectionEnd) {
    contentToInsert = editorContent.value.substring(textarea.selectionStart, textarea.selectionEnd);
  }
  
  newMessage.value = contentToInsert; // Insert into chat input
};

// Chat Logic
const renderMarkdown = (text) => {
  let processedText = text.replace(/```(\w*)\s*([\s\S]*?)```/g, (match, lang, code) => {
    return '```' + lang + '\n' + code.trim() + '\n```';
  });
  return marked.parse(processedText);
};

const messagesContainer = ref(null);

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
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
  scrollToBottom(); // Scroll down after user sends message
  const userMessage = newMessage.value;
  newMessage.value = '';

  isLoading.value = true;
  currentStatus.value = 'Typing...'; // Initial status
  currentStreamingMessage.value = ''; // Clear previous streaming message

  try {
    for await (const chunk of sendMessageToApi(userMessage, appName, userId, currentSessionId.value)) {
      if (chunk.type === 'status') {
        currentStatus.value = chunk.message;
      } else if (chunk.type === 'text') {
        for (let i = 0; i < chunk.content.length; i++) {
          currentStreamingMessage.value += chunk.content[i];
          scrollToBottom();
          await new Promise(resolve => setTimeout(resolve, 10)); // Small delay for typing effect
        }
      }
    }
  } catch (error) {
    console.error('Error sending message:', error);
    messages.value.push({ text: 'Error: Could not get a response.', sender: 'bot' });
  } finally {
    isLoading.value = false;
    if (currentStreamingMessage.value) {
      messages.value.push({ text: currentStreamingMessage.value, sender: 'bot' });
    }
    currentStatus.value = ''; // Clear status after response
    currentStreamingMessage.value = ''; // Clear streaming message after response
    scrollToBottom(); // Scroll one last time after response is complete
  }
};
</script>

<style scoped>
.combined-container {
  display: flex;
  width: 100vw;
  height: 100vh;
}

.editor-panel {
  display: flex;
  flex-direction: column;
  padding: 10px;
  border-right: 1px solid #ccc;
  width: 40%; /* Adjust as needed */
  height: 100%;
  box-sizing: border-box;
}

.editor-wrapper {
  display: flex;
  flex-grow: 1;
  margin-bottom: 10px;
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden; /* Ensures line numbers and textarea stay within bounds */
}

.line-numbers {
  background-color: #f0f0f0;
  padding: 10px 5px;
  text-align: right;
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Andale Mono', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
  line-height: 1.4;
  color: #888;
  user-select: none; /* Prevent selection of line numbers */
  overflow-y: hidden; /* Hide scrollbar, synchronized with textarea */
  flex-shrink: 0; /* Prevent shrinking */
}

.line-numbers span {
  display: block;
}

textarea {
  flex-grow: 1;
  padding: 10px;
  border: none; /* Remove individual border, wrapper handles it */
  border-radius: 0; /* Remove individual border-radius */
  outline: none;
  resize: none; /* Prevent manual resizing */
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Andale Mono', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
  line-height: 1.4;
  white-space: pre; /* Preserve whitespace for alignment */
  overflow-y: auto; /* Allow textarea to scroll */
}

.chat-panel {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  height: 100%;
  max-width: 1000px; /* Increased max-width */
  margin: 0 auto;
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

.insert-button {
  padding: 10px 20px;
  background-color: #007bff; /* Blue background */
  color: white; /* White font */
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.insert-button:hover {
  background-color: #0056b3; /* Darker blue on hover */
}

.message.bot.loading {
  background-color: #f0f0f0;
  color: #666;
  font-style: italic;
}

.message.bot.streaming-message {
  background-color: #e2e2e2;
  color: #333;
  margin-right: auto;
  border-radius: 15px;
  padding: 8px 12px;
  margin-bottom: 8px;
  max-width: 90%;
  word-wrap: break-word;
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
  overflow-y: auto; /* Add vertical scroll for long code blocks */
  max-height: 300px; /* Limit height of code blocks */
  white-space: pre-wrap; /* Ensures long lines wrap */
  word-wrap: break-word; /* Ensures long words break */
  overflow-wrap: break-word; /* Newer alternative to word-wrap */
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