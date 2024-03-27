<script setup lang="ts">
import ImageInput from "./ImageInput.vue";
</script>

<template>
    <div id="main-view" class="view">
        <ImageInput />
    </div>
</template>

<style scoped>
#main-view {
    width: 100vw;
    height: 100vh;          /* added for compatibility */
    height: 100dvh;
    display: flex;
    flex-direction: column;
    flex-wrap: nowrap;
}
</style>