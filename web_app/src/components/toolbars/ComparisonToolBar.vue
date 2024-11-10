<script setup lang="ts">
import "./ImageViewToolBar.css";
import VButton from "primevue/button";
import VDialog from "primevue/dialog";
import VSidebar from "primevue/sidebar";
import QuantitiesEntry from "../QuantitiesEntry.vue";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { computed, ref } from "vue";
import { config, endpoints } from "@/config";
import { parseClassificationsFromResponse, sendRequest } from "@/utils";
import { type DatasetListItem } from "@/types";
import DatasetListItemComponent from "../DatasetListItem.vue";


const imageState = useImageStateStore();
const viewState = useViewStateStore();

const quantitiesVisible = ref<boolean>(false);
const datasetDialogVisible = ref<boolean>(false);
const compareDialogVisible = ref<boolean>(false);
const userDatasets = ref<DatasetListItem[]>([]);
const classifications = computed(() => imageState.objectClassifications);


function handleReturnClick() {
    viewState.setState(ViewStates.ImageEditPoints);
    viewState.showBackground = true;
    viewState.isEditingExistingResult = true;
    imageState.clearResult();
}


function handleCompareClick() {
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
            compareDialogVisible.value = true;
        }
        else {
            console.error("Failed to retrieve datasets");
        }
    });
}


function compareWithDataset(datasetId: number) {
    const requestUri = config.serverUri + endpoints.compareToDataset
            .replace("{result_id}", imageState.resultId.toString())
            .replace("{dataset_id}", datasetId.toString());
    const requestPromise = sendRequest(requestUri, null, "GET");

    viewState.isWaitingForResponse = true;
    compareDialogVisible.value = false;
    requestPromise.then((response) => {
        if (response.status === 200) {
            console.log("Comparison successful");
            imageState.clearResult();
            parseClassificationsFromResponse(response.data.classifications);
            datasetDialogVisible.value = false;
        }
        else {
            console.error("Comparison failed");
        }

        viewState.isWaitingForResponse = false;
    });
}
</script>


<template>
    <div class="image-view-tool-bar bar">
        <VButton text label="Adjust" icon="pi pi-pencil" @click="handleReturnClick();" />
        <div class="element-count">
            <span class="element-count-value">{{ imageState.imageElements.length }}</span>
            <span class="element-count-label">Elements</span>
        </div>
        <VButton text label="Details" icon="pi pi-list" @click="quantitiesVisible = true" />
    </div>
    <VButton :class="(viewState.isWaitingForResponse ? 'inactive-button ' : '') + 'compare-button'"
            label="Compare with dataset" @click="handleCompareClick" />
    <VSidebar v-model:visible="quantitiesVisible" position="bottom" style="height: auto" class="quantities" header="Counted elements">
        <div class="quantities-label-notice notice">You can toggle label visibility in the settings</div>
        <div class="quantities-header">
            <div class="quantities-col">Count</div>
            <div class="quantities-col">Label<span class="rename-notice notice">(tap to rename)</span></div>
            <div class="quantities-col">Show boxes</div>
        </div>
        <div class="quantities-content">
            <QuantitiesEntry v-for="(quantity, index) in classifications" :key="index" :index="quantity.index" />
            <div v-if="classifications.length === 0" class="no-elements-notice notice">(no elements found)</div>
        </div>
    </VSidebar>
    <VDialog v-model:visible="compareDialogVisible" modal header="Select dataset" class="compare-dialog"
            :dismissable-mask="true" :draggable="false">
        <div class="compare-dataset-list">
            <div v-for="(dataset, index) in userDatasets.sort((a, b) => b.timestamp - a.timestamp)" :key="index">
                <DatasetListItemComponent v-bind="dataset" />
                <VButton text label="Select" class="compare-select" @click="compareWithDataset(dataset.id)" />
            </div>
        </div>
        <div class="dialog-controls">
            <VButton outlined label="Cancel" @click="compareDialogVisible = false" />
        </div>
    </VDialog>
</template>


<style scoped>
.compare-dialog .dialog-controls {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

.compare-button {
    position: fixed;
    bottom: 130px;
    left: 50%;
    transform: translateX(-50%);
    max-width: 240px;
    width: 100%;
}

.compare-dialog .compare-dataset-list {
    max-height: 65vh;
    overflow-y: auto;
    margin-bottom: 18px;
}

.compare-dialog .compare-dataset-list > div {
    position: relative;
}

.compare-dialog .compare-dataset-list > div:not(:last-child) {
    border-bottom: 1px solid var(--surface-border);
}

.inactive-button {
    pointer-events: none;
    opacity: 0.5;
}

.compare-select {
    position: absolute;
    top: 50%;
    right: 6px;
    transform: translateY(-50%);
}
</style>
