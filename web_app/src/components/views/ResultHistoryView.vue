<script setup lang="ts">
import VButton from "primevue/button";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { default as ResultHistoryItemComponent } from "../ResultHistoryItem.vue";
import type { ResultHistoryItem } from "@/types/app";
import { base64ToImageUri } from "@/utils";
import SettingsWidget from "../SettingsWidget.vue";
import LoadingSpinner from "../LoadingSpinner.vue";
import { onMounted, ref } from "vue";
import { getResults, getResultsThumbnails } from "@/requests/results";


// todo: pagination


const viewState = useViewStateStore();

const historyItems = ref<ResultHistoryItem[]>([]);


function onBack() {
    viewState.setState(ViewStates.UserView);
}


onMounted(async () => {
    viewState.isWaitingForResponse = true;

    await getResults().then((response) => {
        for (const item of response) {
            const historyItem: ResultHistoryItem = {
                id: item.id,
                imageId: item.image_id,
                timestamp: Date.parse(item.timestamp),
                classificationCount: item.data.classifications.length,
                elementCount: item.data.count
            };

            historyItems.value.push(historyItem);
        }
    }).catch(() => {
        viewState.setState(ViewStates.UserView);
    });

    await getResultsThumbnails().then((response) => {
        for (const item of response) {
            const historyItem = historyItems.value.find((historyItem) => historyItem.id == item.id);
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
    <div id="result-history-view" class="view">
        <div class="history-view-nav-bar nav-bar bar">
            <div class="nav-bar-content bar-content">
                <VButton text rounded icon="pi pi-chevron-left" @click="onBack()" />
                <h2>Counting history</h2>
                <SettingsWidget />
            </div>
        </div>
        <div class="result-history-items">
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
    user-select: none;
    max-height: calc(100vh - 55px);
    max-width: 768px;
    margin: 55px auto 0 auto;
}

#result-history-view {
    overflow: auto;
}

#result-history-view .notice {
    text-align: center;
}

@media screen and (min-width: 340px) {
    .result-history-items {
        margin-top: 70px;
    }

    .history-view-nav-bar h2 {
        font-size: 1.4rem;
    }
}

@media screen and (min-width: 380px) {
    .history-view-nav-bar h2 {
        font-size: 1.5rem;
    }
}
</style>
