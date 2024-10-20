<script setup lang="ts">
import VButton from "primevue/button";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { default as ResultHistoryItemComponent } from "../ResultHistoryItem.vue";
import type { ResultHistoryItem } from "@/types";
import { onMounted, ref } from "vue";
import { config, endpoints } from "@/config";
import { sendRequest, type Response } from "@/utils";

const viewState = useViewStateStore();

const itemsLoaded = ref<boolean>(false);
const historyItems = ref<ResultHistoryItem[]>([]);

function onBack() {
    viewState.setState(ViewStates.UserView);
}

onMounted(async () => {
    const requestUri = config.serverUri + endpoints.results;
    
    const requestPromise = sendRequest(requestUri, null, "GET");
    requestPromise.then((response: Response) => {
        if (response.status != 200) {
            console.error("Failed to load result history items");
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

            // const imageRequestUri = config.serverUri + endpoints.getImage.replace("{image_id}", item.image_id);
            // const imageRequestPromise = sendRequest(imageRequestUri, null, "GET");
            // imageRequestPromise.then((imageResponse: Response) => {
            //     if (imageResponse.status != 200) {
            //         console.error("Failed to load image for result history item");
            //         return;
            //     }
            //     historyItem.imageUri = imageResponse.data;
            // });

            historyItems.value.push(historyItem);
        }
    });
});
</script>


<template>
    <div id="result-history-view" class="view">
        <div class="history-view-nav-bar nav-bar bar">
            <VButton text rounded icon="pi pi-chevron-left" @click="onBack()" />
            <h2 id="history-view-title">Result history</h2>
            <VButton text rounded icon="pi pi-cog" @click="onBack()" />
        </div>
        <div class="result-history-items">
            <ResultHistoryItemComponent v-for="(item, index) in historyItems.sort((a, b) => a.timestamp - b.timestamp)"
                    :key="index" v-bind="item" />
        </div>
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
    gap: 20px;
    padding: 20px;
    margin-top: 55px;
    overflow: auto;
    user-select: none;
    max-height: calc(100vh - 55px);
}
</style>
