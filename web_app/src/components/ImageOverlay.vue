<script setup lang="ts">
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore } from "@/stores/viewState";
import BoundingBox from "./BoundingBox.vue";
import SelectionPoint from "./SelectionPoint.vue";
import { ref, onMounted, computed } from "vue";
import LoadingSpinner from "./LoadingSpinner.vue";
import { config, endpoints } from "@/config";
import { createMaskImage, sendRequest } from "@/utils";


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

    const overlayWidth = overlay.value.clientWidth;                     // Overlay element width
    const overlayHeight = overlay.value.clientHeight;                   // Overlay element height
    const overlayRatio = overlayWidth / overlayHeight;                  // Overlay ratio of width/height
    const srcImageRatio = imageState.width / imageState.height;         // Image ratio of width/height
    let innerImageWidth = 0, innerImageHeight = 0;                      // Dimensions of <img> element (differ from original)
    let destinationHeightFraction = 1, destinationWidthFraction = 1;    // Fractions used for scaling the <img> element dimensions

    // Calculate which <img> element dimension to scale
    if (srcImageRatio > overlayRatio) {
        // Original image wider than <img> element
        destinationHeightFraction = (imageState.height / overlayHeight) / (imageState.width / overlayWidth);
    }
    else {
        // <img> element wider than original image
        destinationWidthFraction = (imageState.width / overlayWidth) / (imageState.height / overlayHeight);
    }

    // Scale <img> element to fit overlay
    innerImageWidth = overlayWidth * destinationWidthFraction;
    innerImageHeight = overlayHeight * destinationHeightFraction;

    // Calculate overlay offsets
    const topMargin = Math.max((overlayHeight - innerImageHeight) / 2, 0);
    const leftMargin = Math.max((overlayWidth - innerImageWidth) / 2, 0);

    // Calculate CSS properties
    innerOverlay.value.style.width = innerImageWidth + "px";
    innerOverlay.value.style.height = innerImageHeight + "px";
    innerOverlay.value.style.top = topMargin + "px";
    innerOverlay.value.style.left = leftMargin + "px";

    // Store current scale/offset info
    imageState.scaledImageWidth = innerImageWidth;
    imageState.scaledImageHeight = innerImageHeight;
    imageState.overlayOffsetLeft = leftMargin;
    imageState.overlayOffsetTop = topMargin;
    if (srcImageRatio > overlayRatio) {
        imageState.boundingBoxScale = innerImageWidth / imageState.width;
    }
    else {
        imageState.boundingBoxScale = innerImageHeight / imageState.height;
    }
}

function sendPoints() {
    if (imageState.points.length === 0) {
        viewState.showBackground = false;
        return;
    }

    const requestUri = config.serverUri + endpoints.sendSelection.replace("{image_id}", imageState.imageId.toString());
    const requestData = JSON.stringify({"data": imageState.points});
    const responsePromise = sendRequest(requestUri, requestData, "PUT");

    viewState.isWaitingForResponse = true;

    // Backend returns a background mask
    responsePromise.then((response) => {
        viewState.isWaitingForResponse = false;

        const maskImageData = createMaskImage(response.data.mask);
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");
        if (ctx == undefined) return;

        viewState.showBackground = true;

        ctx.canvas.width = imageState.width;
        ctx.canvas.height = imageState.height;
        ctx.putImageData(maskImageData, 0, 0);

        const maskImage = new Image();
        maskImage.onload = () => {
            ctx.drawImage(maskImage, 0, 0);
        };

        document.querySelector<HTMLImageElement>("#mask-image")!.src = canvas.toDataURL();
    });
}

function handleOverlayClick(event: MouseEvent) {
    if (imageState.isPanning) return;

    const bbox = (event.target! as HTMLElement).getBoundingClientRect();
    // [x, y] relative to original image size, not scaled
    const x = (event.clientX - bbox.left) / scale.value / imageState.userZoom;
    const y = (event.clientY - bbox.top) / scale.value / imageState.userZoom;
    const beforePointCount = imageState.points.length;

    if (viewState.isAddingPoint) {
        if ((event.target! as HTMLElement).classList.contains("selection-point")) return;
        imageState.addPoint(viewState.isPointTypePositive, x, y);
    }
    else if (viewState.isRemovingPoint) {
        // When clicking a point and not the overlay, mouse coords returned by the event differ
        // If clicked a point, get its coords from data attributes instead of event
        if ((event.target! as HTMLElement).classList.contains("selection-point")) {
            const pointX = Number((event.target! as HTMLElement).getAttribute("data-x"));
            const pointY = Number((event.target! as HTMLElement).getAttribute("data-y"));
            imageState.removeNearbyPoint(pointX, pointY);
        }
        else {
            imageState.removeNearbyPoint(x, y);
        }
    }

    // If point was added or removed, send the updated points to the server
    if (beforePointCount !== imageState.points.length) sendPoints();
}


onMounted(() => {
    scaleOverlay();
    window.addEventListener("resize", scaleOverlay);
});
</script>


<template>
    <div class="img-overlay" ref="overlay">
        <div class="inner-overlay" ref="innerOverlay" style="position: absolute" @click="handleOverlayClick">
            <img id="mask-image" :src="imageState.backgroundMaskDataURL">
            <div class="bounding-boxes">
                <BoundingBox v-for="([, box], index) in Object.entries(elements)" :key="index" v-bind="box" />
            </div>
            <div class="selection-points" v-if="viewState.showPoints">
                <SelectionPoint v-for="([, point], index) in Object.entries(points)" :key="index"
                        v-bind="point" v-bind:class="[point.positive ? 'positive' : 'negative']" />
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
