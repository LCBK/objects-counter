<script setup lang="ts">
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore } from "@/stores/viewState";
import BoundingBox from "./BoundingBox.vue";
import SelectionPoint from "./SelectionPoint.vue";
import { ref, onMounted, onBeforeMount, computed } from "vue";
import { boundingBoxColors } from "@/config";


const imageState = useImageStateStore();
const viewState = useViewStateStore();

const overlay = ref<HTMLDivElement>();
const innerOverlay = ref<HTMLDivElement>();

const results = imageState.results;
const points = imageState.points;

const scale = computed(() => imageState.boundingBoxScale);


function getTransformedCoords() {

}

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

    imageState.scaledImageWidth = innerImageWidth;
    imageState.scaledImageHeight = innerImageHeight;
    imageState.overlayOffsetLeft = left_margin;
    imageState.overlayOffsetTop = top_margin;

    if (srcImageRatio > overlayRatio) {
        imageState.boundingBoxScale = innerImageWidth / imageState.width;
    }
    else {
        imageState.boundingBoxScale = innerImageHeight / imageState.height;
    }
}

function assignClassColors() {
    const assignedClasses: Array<string> = [];
    const assignedColors: Array<string> = [];

    let colorIndex = 0;
    imageState.results.forEach((box) => {
        if (!assignedClasses.includes(box.class)) {
            let newColor = boundingBoxColors[colorIndex % boundingBoxColors.length];
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
}

function handleOverlayClick(event: MouseEvent) {
    const headerHeight = document.querySelector(".image-view-nav-bar")!.clientHeight;
    const x = (event.clientX - imageState.overlayOffsetLeft) / scale.value;
    const y = (event.clientY - imageState.overlayOffsetTop - headerHeight) / scale.value;
    if (viewState.isAddingPoint) {
        imageState.addPoint(true, x, y);
    }
    else if (viewState.isRemovingPoint) {
        imageState.removePoint(x, y);
    }
}


onBeforeMount(() => {
    assignClassColors();
})

onMounted(() => {
    scaleOverlay();
    window.addEventListener("resize", scaleOverlay);
});
</script>


<template>
    <div class="img-overlay" ref="overlay">
        <div class="inner-overlay" ref="innerOverlay" style="position: absolute"
                @click="handleOverlayClick">
            <BoundingBox v-for="([, box], index) in Object.entries(results)" :key="index"
                    v-bind:top-left="box.top_left" v-bind:bottom-right="box.bottom_right"
                    v-bind:certainty="box.certainty" v-bind:class="box.class"
                    v-bind:index="index" v-bind:color="box.color" />
            <SelectionPoint v-for="([, point], index) in Object.entries(points)" :key="index"
                    v-bind:is-positive="true" v-bind:position="point.position" />
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
