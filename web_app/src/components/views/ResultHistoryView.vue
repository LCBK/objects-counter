<script setup lang="ts">
import "./HistoryView.css";
import VButton from "primevue/button";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { default as ResultHistoryItemComponent } from "../ResultHistoryItem.vue";
import type { ResultHistoryItem } from "@/types/app";
import { base64ToImageUri } from "@/utils";
import SettingsWidget from "../SettingsWidget.vue";
import LoadingSpinner from "../LoadingSpinner.vue";
import { onMounted, ref } from "vue";
import { getResults, getResultsThumbnails } from "@/requests/results";


const viewState = useViewStateStore();

const historyItems = ref<ResultHistoryItem[]>([]);


function onBack() {
    viewState.setState(ViewStates.UserView);
}


onMounted(async () => {
    viewState.isWaitingForResponse = true;

    await getResults().then(response => {
        for (const item of response) {
            const historyItem: ResultHistoryItem = {
                id: item.id,
                images: item.images,
                timestamp: Date.parse(item.timestamp)
            };

            historyItems.value.push(historyItem);
        }
    }).catch(() => {
        viewState.setState(ViewStates.UserView);
    });

    await getResultsThumbnails().then(response => {
        for (const item of response) {
            const historyItem = historyItems.value.find(historyItem => historyItem.id == item.id);
            if (historyItem) {
                historyItem.thumbnailUri = base64ToImageUri(item.thumbnail);
            }
        }
    }).finally(() => {
        viewState.isWaitingForResponse = false;
    });
});
</script>


<template>
    <div id="result-history-view" class="history-view view">
        <div class="history-view-nav-bar nav-bar bar">
            <div class="nav-bar-content bar-content">
                <VButton text rounded icon="pi pi-chevron-left" @click="onBack()" />
                <h2>Counting history</h2>
                <SettingsWidget />
            </div>
        </div>
        <div class="result-history-items history-items">
            <ResultHistoryItemComponent v-for="(item, index) in historyItems.sort((a, b) => b.timestamp - a.timestamp)"
                    :key="index" v-bind="item" />
        </div>
        <p v-if="historyItems.length === 0" class="notice">no items to show</p>
        <Transition name="waiting-overlay">
            <div v-if="viewState.isWaitingForResponse" class="waiting-overlay">
                <LoadingSpinner />
            </div>
        </Transition>
    </div>
</template>
