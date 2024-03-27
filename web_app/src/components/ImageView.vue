<script setup lang="ts">
import ImageDisplay from "./ImageDisplay.vue";
import ImageViewBar from "./ImageViewBar.vue";
</script>

<template>
    <div id="image-view" class="view">
        <ImageViewBar />
        <ImageDisplay />
    </div>
</template>

<style scoped>
#image-view {
    width: 100vw;
    height: 100vh;
    height: 100dvh;
}
</style>