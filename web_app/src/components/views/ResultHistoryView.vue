<script setup lang="ts">
import VButton from "primevue/button";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { default as ResultHistoryItemComponent } from "../ResultHistoryItem.vue";
import type { ResultHistoryItem } from "@/types";
import { config, endpoints } from "@/config";
import { base64ToImageUri, sendRequest, type Response } from "@/utils";
import SettingsWidget from "../SettingsWidget.vue";
import LoadingSpinner from "../LoadingSpinner.vue";
import { onMounted, ref } from "vue";


// todo: pagination


const viewState = useViewStateStore();

const historyItems = ref<ResultHistoryItem[]>([]);


function onBack() {
    viewState.setState(ViewStates.UserView);
}


onMounted(async () => {
    const resultsRequestUri = config.serverUri + endpoints.getResults;
    const resultsRequestPromise = sendRequest(resultsRequestUri, null, "GET");
    viewState.isWaitingForResponse = true;
    resultsRequestPromise.then((response: Response) => {
        if (response.status != 200) {
            console.error("Failed to load result history items");
            viewState.setState(ViewStates.UserView);
            return;
        }

        const responseItems = response.data;
        for (const item of responseItems) {
            const historyItem: ResultHistoryItem = {
                id: item.id,
                imageId: item.image_id,
                timestamp: Date.parse(item.timestamp),
                classificationCount: item.data.classifications.length,
                elementCount: item.data.count
            };

            historyItems.value.push(historyItem);
        }
    });

    const thumbnailsRequestUri = config.serverUri + endpoints.getResultsThumbnails;
    const thumbnailsRequestPromise = sendRequest(thumbnailsRequestUri, null, "GET");
    thumbnailsRequestPromise.then((response: Response) => {
        if (response.status != 200) {
            console.error("Failed to load result history thumbnails");
            return;
        }

        const responseItems = response.data;
        for (const item of responseItems) {
            const historyItem = historyItems.value.find((historyItem) => historyItem.id == item.id);
            if (historyItem) {
                historyItem.thumbnailUri = base64ToImageUri(item.thumbnail);
            }
        }
    });

    viewState.isWaitingForResponse = false;
});
</script>


<template>
    <div id="result-history-view" class="view">
        <div class="history-view-nav-bar nav-bar bar">
            <VButton text rounded icon="pi pi-chevron-left" @click="onBack()" />
            <h2>Result history</h2>
            <SettingsWidget />
        </div>
        <div class="result-history-items">
            <ResultHistoryItemComponent v-for="(item, index) in historyItems.sort((a, b) => b.timestamp - a.timestamp)"
                    :key="index" v-bind="item" />
        </div>
        <Transition name="waiting-overlay">
            <div v-if="viewState.isWaitingForResponse" class="waiting-overlay">
                <LoadingSpinner />
            </div>
        </Transition>
    </div>
</template>


<style scoped>
.history-view-nav-bar h2 {
    color: var(--primary-color);
    font-size: 1.3rem;
    line-height: 38px;
    letter-spacing: 0.4px;
    font-weight: 600;
}

.result-history-items {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 16px;
    padding: 16px;
    margin-top: 55px;
    overflow: auto;
    user-select: none;
    max-height: calc(100vh - 55px);
}
</style>
