<script setup lang="ts">
import { config, endpoints } from "@/config";
import { useImageStateStore } from "@/stores/imageState";
import { ImageAction, useViewStateStore, ViewStates } from "@/stores/viewState";
import { parseClassificationsFromResponse, sendRequest } from "@/utils";
import { type Response } from "@/utils";
import { defineProps } from "vue";


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


function onResultClick() {
    const imageRequestUri = config.serverUri + endpoints.getImage.replace("{image_id}", props.imageId.toString());
    const imageRequestPromise = sendRequest(imageRequestUri, null, "GET", "application/json", false);
    viewState.isWaitingForResponse = true;
    imageRequestPromise.then((imageResponse: Response) => {
        if (imageResponse.status != 200) {
            console.error("Failed to load image for result history item");
            return;
        }

        imageResponse.data.blob()
            .then((blob: Blob) => { return URL.createObjectURL(blob); })
            .then((url: string) => {
                imageState.url = url;
                imageState.imageId = props.imageId;

                const img = new Image;
                img.src = url;
                img.onload = () => {
                    imageState.width = img.width;
                    imageState.height = img.height;
                };
            });

    });

    const resultRequestUri = config.serverUri + endpoints.getResult.replace("{result_id}", props.id.toString());
    const resultRequestPromise = sendRequest(resultRequestUri, null, "GET");
    resultRequestPromise.then((resultResponse: Response) => {
        if (resultResponse.status != 200) {
            console.error("Failed to load result for result history item");
            return;
        }

        const resultData = resultResponse.data.data;
        parseClassificationsFromResponse(resultData.classifications);
        imageState.resultId = props.id;

        viewState.isWaitingForResponse = false;
        viewState.setState(ViewStates.ImageViewResult);
    });
}
</script>


<template>
    <div class="result-history-item" @click="onResultClick()">
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
</style>

<style>
.result-counts .pi {
    margin-right: 0;
}
</style>
