<script setup>
import Chat from './components/Chat.vue';
</script>

<template>
  <Chat />
</template>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  overflow: hidden; /* Prevent body scroll */
}

.app-container {
  display: flex;
  width: 100vw;
  height: 100vh;
}
</style>