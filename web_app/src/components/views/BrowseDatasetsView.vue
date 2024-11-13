<script setup lang="ts">
import VButton from "primevue/button";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import type { DatasetListItem } from "@/types";
import { config, endpoints } from "@/config";
import { base64ToImageUri, sendRequest, type Response } from "@/utils";
import SettingsWidget from "../SettingsWidget.vue";
import { onMounted, ref } from "vue";
import DatasetListItemComponent from "../DatasetListItem.vue";
import LoadingSpinner from "../LoadingSpinner.vue";



const viewState = useViewStateStore();

const userDatasets = ref<DatasetListItem[]>([]);


function onBack() {
    viewState.setState(ViewStates.UserView);
}

function loadDatasets() {
    const datasetRequestUri = config.serverUri + endpoints.getDatasets;
    const datasetRequestPromise = sendRequest(datasetRequestUri, null, "GET");
    viewState.isWaitingForResponse = true;
    datasetRequestPromise.then((response) => {
        if (response.status === 200) {
            userDatasets.value = [];
            for (const dataset of response.data) {
                userDatasets.value.push({
                    id: dataset.id,
                    name: dataset.name,
                    timestamp: Date.parse(dataset.timestamp)
                } as DatasetListItem);
            }
        }
        else {
            console.error("Failed to retrieve datasets");
        }
    });

    const thumbnailsRequestUri = config.serverUri + endpoints.getDatasetsThumbnails;
    const thumbnailsRequestPromise = sendRequest(thumbnailsRequestUri, null, "GET");
    thumbnailsRequestPromise.then((response: Response) => {
        if (response.status != 200) {
            console.error("Failed to load result history thumbnails");
            return;
        }

        const responseItems = response.data;
        for (const item of responseItems) {
            const datasetItem = userDatasets.value.find((datasetItem) => datasetItem.id == item.id) as DatasetListItem;
            if (datasetItem) {
                datasetItem.thumbnailUri = base64ToImageUri(item.thumbnail);
            }
        }

        viewState.isWaitingForResponse = false;
    });
}


onMounted(async () => {
    loadDatasets();
});
</script>


<template>
    <div id="browse-datasets-view" class="view">
        <div class="browse-datasets-view-nav-bar nav-bar bar">
            <VButton text rounded icon="pi pi-chevron-left" @click="onBack()" />
            <h2>Browse datasets</h2>
            <SettingsWidget />
        </div>
        <p class="browse-datasets-notice notice">tap on a dataset to view details</p>
        <div class="browse-datasets-list">
            <DatasetListItemComponent v-for="(dataset, index) in userDatasets.sort((a, b) => b.timestamp - a.timestamp)"
                    :key="index" v-bind="dataset" @data-changed="loadDatasets" />
        </div>
        <p v-if="userDatasets.length === 0" class="notice">no items to show</p>
        <Transition name="waiting-overlay">
            <div v-if="viewState.isWaitingForResponse" class="waiting-overlay">
                <LoadingSpinner />
            </div>
        </Transition>
    </div>
</template>


<style scoped>
.browse-datasets-view-nav-bar h2 {
    color: var(--primary-color);
    font-size: 1.3rem;
    line-height: 38px;
    letter-spacing: 0.4px;
    font-weight: 600;
}

.browse-datasets-list {
    padding: 0 20px 8px 20px;
    max-height: calc(100vh - 91px);
    overflow-y: auto;
}

.browse-datasets-list > *:not(:last-child) {
    border-bottom: 1px solid var(--surface-border);
}

.browse-datasets-notice {
    font-size: 0.8rem;
    text-align: center;
    margin: 63px 0 8px 0;
}

#browse-datasets-view .notice {
    text-align: center;
}
</style>
