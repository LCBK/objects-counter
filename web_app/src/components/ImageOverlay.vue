<script setup lang="ts">
import { useImageStateStore } from "@/stores/imageState";
import BoundingBox from "./BoundingBox.vue";
import { ref, onMounted, onBeforeMount } from "vue";
import { boundingBoxColors } from "@/config";


const imageState = useImageStateStore();
const overlay = ref<HTMLDivElement>();
const innerOverlay = ref<HTMLDivElement>();
const results = imageState.results;


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

onBeforeMount(() => {
    // Determine class colors
    let colorIndex = 0;
    let assignedClasses: Array<string> = [];
    let assignedColors: Array<string> = [];
    imageState.results.forEach((box) => {
        if (!assignedClasses.includes(box.class)) {
            let newColor = boundingBoxColors[colorIndex % boundingBoxColors.length]
            assignedClasses.push(box.class);
            assignedColors.push(newColor);
            colorIndex++;
            box.color = newColor;
        }
        else {
            let colorIndex = assignedClasses.indexOf(box.class);
            box.color = assignedColors[colorIndex];
        }
    });
})

onMounted(() => {
    scaleOverlay();
    window.addEventListener("resize", scaleOverlay);
});
</script>


<template>
    <div class="img-overlay" ref="overlay">
        <div class="inner-overlay" ref="innerOverlay" style="position: absolute">
            <BoundingBox v-for="([, box], index) in Object.entries(results)" :key="index"
                v-bind:top-left="box.top_left" v-bind:bottom-right="box.bottom_right"
                v-bind:certainty="box.certainty" v-bind:class="box.class"
                v-bind:index="index" v-bind:color="box.color" />
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
