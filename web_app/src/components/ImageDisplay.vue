<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useImageStateStore } from "@/stores/imageState";
import ImageOverlay from "./ImageOverlay.vue";
import Panzoom from "../../node_modules/@panzoom/panzoom/";


const imageState = useImageStateStore();
const displayContainer = ref<HTMLDivElement>();
const displayedImage = ref<HTMLImageElement>();


onMounted(() => {
    if (!displayedImage.value || imageState.url === "" ||
        imageState.url === null || imageState.url === undefined) return;

    displayedImage.value.src = imageState.url;

    const panzoom = Panzoom(displayContainer.value!, {
        minScale: 1,
        maxScale: 5,
        step: 0.5,
        duration: 0,
        noBind: true            // we are manually binding events below, prevent double binding
    })

    displayContainer.value!.addEventListener('pointerdown', (event) => {
        imageState.isPanning = false;
        panzoom.handleDown(event);
    });

    document.addEventListener('pointermove', (event) => {
        imageState.isPanning = true;
        panzoom.handleMove(event);
    });

    document.addEventListener('pointerup', (event) => {
        panzoom.handleUp(event);
    });

    displayContainer.value!.addEventListener("panzoomchange", () => {
        imageState.userZoom = panzoom.getScale();
    });

    displayContainer.value!.parentElement!.addEventListener('wheel', (event) => {
        if (!event.shiftKey) return;
        panzoom.zoomWithWheel(event);
    });
});
</script>


<template>
    <div class="image-display" ref="displayContainer">
        <img id="displayed-image" alt="Uploaded image" ref="displayedImage" />
        <ImageOverlay />
    </div>
</template>


<style scoped>
.image-display {
    overflow: hidden;
    position: relative;
    height: calc(100% - 144px);
    top: 54px;
}

.image-display img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    object-position: center;
}
</style>
