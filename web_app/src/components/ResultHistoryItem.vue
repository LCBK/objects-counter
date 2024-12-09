<script setup lang="ts">
import "./HistoryItems.css";
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
    <div class="result-history-item history-item" @click="handleResultClick()">
        <img :src="props.thumbnailUri" alt="No thumbnail" class="item-image" />
        <div class="item-date">{{ date }}</div>
        <div class="item-time">{{ time }}</div>
        <div class="item-counts">
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
