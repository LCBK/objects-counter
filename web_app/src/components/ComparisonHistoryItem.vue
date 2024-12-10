<script setup lang="ts">
import "./HistoryItems.css";
import { getImageBlob } from "@/requests/images";
import { ImageAction, useViewStateStore, ViewStates } from "@/stores/viewState";
import type { ImageWithAllData } from "@/types/requests";
import { parseElementsToImage, processImageData } from "@/utils";
import type { ComparisonDiff } from "@/types/requests";
import type { PropType } from "vue";
import { useImageStateStore } from "@/stores/imageState";


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
    diff: {
        type: Object as PropType<ComparisonDiff>,
        required: true
    },
    timestamp: {
        type: Number,
        required: true
    },
    datasetName: {
        type: String,
        required: true
    }
});

const imageState = useImageStateStore();
const viewState = useViewStateStore();

const date = new Date(props.timestamp).toISOString().split("T")[0];
const time = new Date(props.timestamp).toLocaleTimeString();

const elementCount = props.images.reduce((acc, img) => acc + img.elements.length, 0);
const positiveCount = Object.values(props.diff).filter(v => v > 0).reduce((acc, v) => acc + v, 0);
const negativeCount = Object.values(props.diff).filter(v => v < 0).reduce((acc, v) => acc + v, 0);

async function handleItemClick() {
    viewState.isWaitingForResponse = true;

    for (const image of props.images) {
        await getImageBlob(image.id).then(blob => {
            processImageData(blob, image.id).then(() => {
                parseElementsToImage(image.id, image.elements);
            });
        });
    }

    imageState.comparisonId = props.id;
    imageState.comparisonDifference = props.diff;
    imageState.comparisonDatasetName = props.datasetName;

    viewState.isWaitingForResponse = false;
    viewState.currentAction = ImageAction.CompareWithDataset;
    viewState.setState(ViewStates.ImageViewComparisonResult);
}
</script>


<template>
    <div class="result-history-item history-item" @click="handleItemClick()">
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
            <div v-if="positiveCount === 0 && negativeCount === 0" class="diff-ok">
                <i class="pi pi-check"></i>
            </div>
            <slot v-else>
                <div class="diff-positive">
                    <span class="diff-symbol">+</span>
                    <span class="diff-value">{{ positiveCount }}</span>
                </div>
                <div class="diff-negative">
                    <span class="diff-symbol">-</span>
                    <span class="diff-value">{{ Math.abs(negativeCount) }}</span>
                </div>
            </slot>
        </div>
    </div>
</template>


<style scoped>
.item-counts > div.diff-positive,
.item-counts > div.diff-negative {
    gap: 2px;
}

.diff-symbol {
    font-size: 1.2rem;
    margin-top: -2px;
}

.diff-positive,
.diff-ok {
    color: var(--color-success);
}

.diff-negative {
    color: var(--color-error);
}

@media screen and (min-width: 400px) {
    .diff-symbol {
        font-size: 1.4rem;
    }
}
</style>

<style>
.diff-ok .pi {
    font-weight: 600;
}

@media screen and (min-width: 400px) {
    .result-counts .diff-ok .pi {
        font-size: 1.2rem;
    }
}
</style>
