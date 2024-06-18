<script setup lang="ts">
import { useImageStateStore } from "@/stores/imageState";
import BoundingBox from "./BoundingBox.vue";
import { ref, onMounted } from "vue";


const imageState = useImageStateStore();
const overlay = ref<HTMLDivElement>();
const innerOverlay = ref<HTMLDivElement>();
const results = imageState.result;


function scaleOverlay() {
    if (overlay.value === undefined || overlay.value === null ||
        innerOverlay.value === undefined || innerOverlay.value === null)
        return;

    const imageElement = document.querySelector("#displayed-image") as HTMLImageElement;
    if (!imageElement) return;

    const overlayWidth = overlay.value.clientWidth;
    const overlayHeight = overlay.value.clientHeight;
    const overlayRatio = overlayWidth / overlayHeight;
    const srcImageRatio = imageState.width / imageState.height;
    let innerImageWidth = 0, innerImageHeight = 0;
    let destinationHeightFraction = 0, destinationWidthFraction = 0;

    if (srcImageRatio > overlayRatio) {
        destinationWidthFraction = 1;
        destinationHeightFraction = (imageState.height / overlayHeight) / (imageState.width / overlayWidth);
    }
    else {
        destinationWidthFraction = (imageState.width / overlayWidth) / (imageState.height / overlayHeight);
        destinationHeightFraction = 1;
    }

    innerImageWidth = overlayWidth * destinationWidthFraction;
    innerImageHeight = overlayHeight * destinationHeightFraction;

    const top_margin = Math.max((overlayHeight - innerImageHeight) / 2, 0);
    const left_margin = Math.max((overlayWidth - innerImageWidth) / 2, 0);

    innerOverlay.value.style.width = innerImageWidth + "px";
    innerOverlay.value.style.height = innerImageHeight + "px";
    innerOverlay.value.style.top = top_margin + "px";
    innerOverlay.value.style.left = left_margin + "px";

    if (srcImageRatio > overlayRatio) {
        imageState.boundingBoxScale = innerImageWidth / imageState.width;
    }
    else {
        imageState.boundingBoxScale = innerImageHeight / imageState.height;
    }
}

onMounted(() => {
    scaleOverlay();
    window.addEventListener("resize", scaleOverlay);
});
</script>


<template>
    <div class="img-overlay" ref="overlay">
        <div class="inner-overlay" ref="innerOverlay" style="position: absolute">
            <BoundingBox v-for="b in results" :key="b.top_left[0]"
                v-bind:top-left="b.top_left" v-bind:bottom-right="b.bottom_right"
                v-bind:certainty="b.certainty" v-bind:class="b.class" />
        </div>
    </div>
</template>


<style scoped>
.img-overlay {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
}
</style>
