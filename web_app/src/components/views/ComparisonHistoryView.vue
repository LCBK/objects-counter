<script setup lang="ts">
import "./HistoryView.css";
import VButton from "primevue/button";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { default as ComparisonHistoryItemComponent } from "../ComparisonHistoryItem.vue";
import type { ComparisonHistoryItem } from "@/types/app";
import { base64ToImageUri } from "@/utils";
import SettingsWidget from "../SettingsWidget.vue";
import LoadingSpinner from "../LoadingSpinner.vue";
import { onMounted, ref } from "vue";
import { getComparisonHistory, getComparisonHistoryThumbnails } from "@/requests/comparisons";


const viewState = useViewStateStore();

const historyItems = ref<ComparisonHistoryItem[]>([]);


function onBack() {
    viewState.setState(ViewStates.UserView);
}


onMounted(async () => {
    viewState.isWaitingForResponse = true;

    await getComparisonHistory().then(response => {
        for (const item of response) {
            const historyItem: ComparisonHistoryItem = {
                id: item.id,
                images: item.images,
                timestamp: Date.parse(item.timestamp),
                diff: item.diff
            };

            historyItems.value.push(historyItem);
        }
    }).catch(() => {
        viewState.setState(ViewStates.UserView);
    });

    await getComparisonHistoryThumbnails().then(response => {
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
    <div id="comparison-history-view" class="history-view view">
        <div class="history-view-nav-bar nav-bar bar">
            <div class="nav-bar-content bar-content">
                <VButton text rounded icon="pi pi-chevron-left" @click="onBack()" />
                <h2>Comparison history</h2>
                <SettingsWidget />
            </div>
        </div>
        <div class="comparison-history-items history-items">
            <ComparisonHistoryItemComponent v-for="(item, index) in historyItems.sort((a, b) => b.timestamp - a.timestamp)"
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
