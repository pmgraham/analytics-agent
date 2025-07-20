<template>
  <div class="chat-container">
    <div class="messages">
      <div v-for="(message, index) in messages" :key="index" :class="['message', message.sender]">
        {{ message.text }}
      </div>
    </div>
    <div class="input-area">
      <input
        v-model="newMessage"
        @keyup.enter="sendMessage"
        placeholder="Type your message..."
      />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { sendMessageToApi, createSession } from '../api';

const messages = ref([]);
const newMessage = ref('');
const currentSessionId = ref(null);
const appName = "agent"; // Define appName
const userId = "default-user"; // Define userId

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

  try {
    const apiResponse = await sendMessageToApi(userMessage, appName, userId, currentSessionId.value);
    messages.value.push({ text: apiResponse, sender: 'bot' });
  } catch (error) {
    console.error('Error sending message:', error);
    messages.value.push({ text: 'Error: Could not get a response.', sender: 'bot' });
  }
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
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
  max-width: 70%;
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

.input-area button:hover {
  background-color: #218838;
}
</style>
