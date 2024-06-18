<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useImageStateStore } from "../stores/imageState";
import BoundingBox from "./BoundingBox.vue";


const imageState = useImageStateStore();
const displayedImage = ref<HTMLImageElement>();
const results = imageState.result;

onMounted(() => {
    if (!displayedImage.value || imageState.url === "" ||
        imageState.url === null || imageState.url === undefined) return;

    displayedImage.value.src = imageState.url;
});
</script>


<template>
    <div class="image-display">
        <img id="displayed-image" alt="Uploaded image" ref="displayedImage" src="../assets/logo.svg" />
        <div class="bounding-boxes">
            <BoundingBox v-for="b in results" :key="b.top_left[0]"
                v-bind:top-left="b.top_left" v-bind:bottom-right="b.bottom_right"
                v-bind:certainty="b.certainty" v-bind:class="b.class" />
        </div>
    </div>
</template>


<style scoped>
.image-display {
    overflow: hidden;
    position: relative;
}

.image-display img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    object-position: center;
}

.bounding-boxes {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
}
</style>
