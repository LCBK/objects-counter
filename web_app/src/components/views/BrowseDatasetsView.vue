<script setup lang="ts">
import VButton from "primevue/button";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import type { DatasetListItem } from "@/types";
import { config, endpoints } from "@/config";
import { sendRequest } from "@/utils";
import SettingsWidget from "../SettingsWidget.vue";
import { onMounted, ref } from "vue";
import DatasetListItemComponent from "../DatasetListItem.vue";



const viewState = useViewStateStore();

const userDatasets = ref<DatasetListItem[]>([]);


function onBack() {
    viewState.setState(ViewStates.UserView);
}


onMounted(async () => {
    const datasetRequestUri = config.serverUri + endpoints.getDatasets;
    const datasetRequestPromise = sendRequest(datasetRequestUri, null, "GET");

    datasetRequestPromise.then((response) => {
        if (response.status === 200) {
            // TODO: add thumbnails to dataset list
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
});
</script>


<template>
    <div id="browse-datasets-view" class="view">
        <div class="browse-datasets-view-nav-bar nav-bar bar">
            <VButton text rounded icon="pi pi-chevron-left" @click="onBack()" />
            <h2>Browse datasets</h2>
            <SettingsWidget />
        </div>
        <p class="browse-datasets-notice">tap on a dataset to view details</p>
        <div class="browse-datasets-list">
            <DatasetListItemComponent v-for="(dataset, index) in userDatasets.sort((a, b) => b.timestamp - a.timestamp)"
                    :key="index" v-bind="dataset" />
        </div>
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
    padding: 0 24px 8px 24px;
    max-height: calc(100vh - 91px);
    overflow-y: auto;
}

.browse-datasets-list > *:not(:last-child) {
    border-bottom: 1px solid var(--surface-border);
}

.browse-datasets-notice {
    color: var(--text-color-secondary);
    font-size: 0.8rem;
    text-align: center;
    margin: 63px 0 8px 0;
}
</style>
