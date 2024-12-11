<script setup lang="ts">
import "./HistoryItems.css";
import { getImageBlob } from "@/requests/images";
import { useImageStateStore } from "@/stores/imageState";
import { ImageAction, useViewStateStore, ViewStates } from "@/stores/viewState";
import type { ImageWithAllData } from "@/types/requests";
import { parseElementsToImage, processImageData } from "@/utils";


const props = defineProps({
    id: {
        type: Number,
        required: true
    },
    images: {
        type: Array<ImageWithAllData>,
        required: true
    },
    thumbnailUri: {
        type: String,
        required: false
    },
    timestamp: {
        type: Number,
        required: true
    }
});

const imageState = useImageStateStore();
const viewState = useViewStateStore();

const elementCount = props.images.reduce((acc, image) => acc + image.elements.length, 0);
const classificationCount = new Set(props.images.flatMap(
    image => image.elements.map(el => el.classification)
)).size;

const date = new Date(props.timestamp).toISOString().split("T")[0];
const time = new Date(props.timestamp).toLocaleTimeString();


async function handleResultClick() {
    viewState.isWaitingForResponse = true;

    for (const image of props.images) {
        await getImageBlob(image.id).then(blob => {
            processImageData(blob, image.id).then(() => {
                parseElementsToImage(image.id, image.elements);
            });
        });
    }

    imageState.resultId = props.id;

    viewState.isWaitingForResponse = false;
    viewState.currentAction = ImageAction.AutomaticCounting;
    viewState.setState(ViewStates.ImageViewCountingResult);
}
</script>


<template>
    <div class="result-history-item history-item" @click="handleResultClick()">
        <div style="position: relative;">
            <img :src="props.thumbnailUri" alt="No thumbnail" class="item-image" />
            <div class="item-image-count">
                <i class="pi pi-image"></i>
                <span>{{ images.length }}</span>
            </div>
        </div>
        <div class="item-date">{{ date }}</div>
        <div class="item-time">{{ time }}</div>
        <div class="item-counts">
            <div>
                <i class="pi pi-box"></i>
                <div>{{ elementCount }}</div>
            </div>
            <div>
                <i class="pi pi-list"></i>
                <div>{{ classificationCount }}</div>
            </div>
        </div>
    </div>
</template>
