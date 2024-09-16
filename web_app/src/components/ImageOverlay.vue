<script setup lang="ts">
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore } from "@/stores/viewState";
import BoundingBox from "./BoundingBox.vue";
import SelectionPoint from "./SelectionPoint.vue";
import { ref, onMounted, computed, onBeforeUpdate } from "vue";
import { boundingBoxColors } from "@/config";
import LoadingSpinner from "./LoadingSpinner.vue";


const imageState = useImageStateStore();
const viewState = useViewStateStore();

const overlay = ref<HTMLDivElement>();
const innerOverlay = ref<HTMLDivElement>();

const elements = computed(() => imageState.imageElements);
const points = imageState.points;

const scale = computed(() => imageState.boundingBoxScale);
const maskVisibility = computed(() => viewState.showBackground ? "block" : "none");


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
    imageState.imageElements.forEach((box) => {
        if (!assignedClasses.includes(box.classification)) {
            let newColor = boundingBoxColors[colorIndex % boundingBoxColors.length];
            assignedClasses.push(box.classification);
            assignedColors.push(newColor);
            colorIndex++;
            box.color = newColor;
        }
        else {
            let colorIndex = assignedClasses.indexOf(box.classification);
            box.color = assignedColors[colorIndex];
        }
    });
}

function handleOverlayClick(event: MouseEvent) {
    if (imageState.isPanning) return;

    const bbox = (event.target! as HTMLElement).getBoundingClientRect();
    const x = (event.clientX - bbox.left) / scale.value / imageState.userZoom;
    const y = (event.clientY - bbox.top) / scale.value / imageState.userZoom;

    if (viewState.isAddingPoint) {
        if ((event.target! as HTMLElement).classList.contains("selection-point")) return;
        imageState.addPoint(viewState.isPointTypePositive, x, y);
    }
    else if (viewState.isRemovingPoint) {
        if ((event.target! as HTMLElement).classList.contains("selection-point")) {
            const pointX = Number((event.target! as HTMLElement).getAttribute("data-x"));
            const pointY = Number((event.target! as HTMLElement).getAttribute("data-y"));
            imageState.removeNearbyPoint(pointX, pointY);
        }
        else imageState.removeNearbyPoint(x, y);
    }
}


onBeforeUpdate(() => {
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
            <img id="mask-image" :src="imageState.backgroundMaskDataURL">
            <div class="bounding-boxes">
                <BoundingBox v-for="([, box], index) in Object.entries(elements)" :key="index" v-bind="box" />
            </div>
            <div class="selection-points" v-if="viewState.showPoints">
                <SelectionPoint v-for="([, point], index) in Object.entries(points)" :key="index"
                        v-bind="point" v-bind:class="[point.isPositive ? 'positive' : 'negative']" />
            </div>
        </div>
        <Transition name="waiting-overlay">
            <div v-if="viewState.isWaitingForResponse" class="waiting-overlay">
                <LoadingSpinner />
            </div>
        </Transition>
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

.waiting-overlay {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    background: rgba(18, 18, 18, 0.65);
}

.waiting-overlay .loader {
    width: 64px;
    height: 64px;
}

.waiting-overlay-enter-active,
.waiting-overlay-leave-active {
    transition: opacity 0.3s ease;
}

.waiting-overlay-enter-from,
.waiting-overlay-leave-to {
    opacity: 0;
}

#mask-image {
    object-fit: contain;
    width: 100%;
    height: 100%;
    filter: brightness(0) saturate(100%) invert(98%) sepia(97%) saturate(7095%) hue-rotate(312deg) brightness(102%) contrast(96%);
    opacity: 0.5;
    display: v-bind(maskVisibility);
    animation: blink-animation 3s infinite ease-in-out;
}

@keyframes blink-animation {
    0% {
        opacity: 0;
    }
    30% {
        opacity: 0.5;
    }
    70% {
        opacity: 0.5;
    }
    100% {
        opacity: 0;
    }
}
</style>
