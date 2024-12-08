<script setup lang="ts">
import { getImageBlob } from "@/requests/images";
import { getResult } from "@/requests/results";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { parseClassificationsFromResponse, processImageData } from "@/utils";


const props = defineProps({
    id: {
        type: Number,
        required: true
    },
    imageId: {
        type: Number,
        required: true
    },
    thumbnailUri: {
        type: String,
        required: false
    },
    timestamp: {
        type: Number,
        required: true
    },
    classificationCount: {
        type: Number,
        required: true
    },
    elementCount: {
        type: Number,
        required: true
    },
});

const imageState = useImageStateStore();
const viewState = useViewStateStore();

const date = new Date(props.timestamp).toISOString().split("T")[0];
const time = new Date(props.timestamp).toLocaleTimeString();


async function handleResultClick() {
    viewState.isWaitingForResponse = true;

    await getImageBlob(props.imageId).then(blob => {
        processImageData(blob, props.imageId);
    });

    await getResult(props.id).then(response => {
        parseClassificationsFromResponse(response.data.classifications);
        imageState.resultId = props.id;
        viewState.setState(ViewStates.ImageViewCountingResult);
    }).finally(() => {
        viewState.isWaitingForResponse = false;
    });
}
</script>


<template>
    <div class="result-history-item" @click="handleResultClick()">
        <img :src="props.thumbnailUri" alt="No thumbnail" class="result-image" />
        <div class="result-date">{{ date }}</div>
        <div class="result-time">{{ time }}</div>
        <div class="result-counts">
            <div>
                <i class="pi pi-box"></i>
                <div>{{ props.elementCount }}</div>
            </div>
            <div>
                <i class="pi pi-list"></i>
                <div>{{ props.classificationCount }}</div>
            </div>
        </div>
    </div>
</template>


<style scoped>
.result-history-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 8px;
    border: 1px solid var(--surface-border);
    border-radius: 10px;
    color: var(--primary-color);
    width: calc(50% - 8px);
    cursor: pointer;
}

.result-image {
    width: 100%;
    border-radius: 8px;
    margin-bottom: 12px;
    max-width: 256px;
    max-height: 256px;
    aspect-ratio: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
}

.result-date {
    font-size: 1rem;
    font-weight: 500;
    color: var(--text-color);
}

.result-time {
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-color-secondary);
    line-height: 16px;
}

.result-counts {
    width: 100%;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-around;
    margin-top: 10px;
    font-weight: 500;
    font-size: 1rem;
}

.result-counts > div {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 8px;
}

@media screen and (min-width: 400px) {
    .result-counts,
    .result-date {
        font-size: 1.2rem;
    }

    .result-time {
        font-size: 1rem;
    }
}

@media screen and (min-width: 520px) {
    .result-history-item {
        width: calc(33.33% - 12px);
    }
}
</style>

<style>
.result-counts .pi {
    margin-right: 0;
}
</style>
