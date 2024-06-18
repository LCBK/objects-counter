<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useImageStateStore } from "@/stores/imageState";
import ImageOverlay from "./ImageOverlay.vue";


const imageState = useImageStateStore();
const displayedImage = ref<HTMLImageElement>();

onMounted(() => {
    if (!displayedImage.value || imageState.url === "" ||
        imageState.url === null || imageState.url === undefined) return;

    displayedImage.value.src = imageState.url;
});
</script>


<template>
    <div class="image-display">
        <img id="displayed-image" alt="Uploaded image" ref="displayedImage" src="../assets/logo.svg" />
        <ImageOverlay />
    </div>
</template>


<style scoped>
.image-display {
    overflow: hidden;
    position: relative;
    height: calc(100% - 54px);
}

.image-display img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    object-position: center;
}
</style>
