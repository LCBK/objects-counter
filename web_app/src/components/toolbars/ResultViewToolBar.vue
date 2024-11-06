<script setup lang="ts">
import VButton from "primevue/button";
import VDialog from "primevue/dialog";
import VSidebar from "primevue/sidebar";
import VInputText from "primevue/inputtext";
import QuantitiesEntry from "../QuantitiesEntry.vue";
import { useImageStateStore } from "@/stores/imageState";
import { ImageAction, useViewStateStore, ViewStates } from "@/stores/viewState";
import { computed, ref } from "vue";
import { config, endpoints } from "@/config";
import { parseClassificationsFromResponse, sendRequest } from "@/utils";
import { type DatasetListItem } from "@/types";


const imageState = useImageStateStore();
const viewState = useViewStateStore();

const quantitiesVisible = ref<boolean>(false);
const datasetDialogVisible = ref<boolean>(false);
const compareDialogVisible = ref<boolean>(false);
const datasetName = ref<string>("Dataset #" + imageState.imageId);
const userDatasets = ref<DatasetListItem[]>([]);
const classifications = computed(() => imageState.objectClassifications);


function handleReturnClick() {
    viewState.setState(ViewStates.ImageEditPoints);
    viewState.showBackground = true;
    viewState.isEditingExistingResult = true;
    imageState.clearResult();
}


function handleSubmitClick() {
    datasetDialogVisible.value = true;
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
                    timestamp: dataset.timestamp
                } as DatasetListItem);
            }
            compareDialogVisible.value = true;
        }
        else {
            console.error("Failed to retrieve datasets");
        }
    });
}


function submitClassificationLeaders() {
    const classifications = imageState.selectedLeaderIds.map((id) => {
        // TODO: temporary data
        return {
            name: "Leader " + id,
            leader: id,
            elements: [id]
        };
    });

    const requestUri = config.serverUri + endpoints.createDataset;
    const requestData = JSON.stringify({
        image_id: imageState.imageId,
        name: datasetName.value,
        classifications: classifications
    });
    const requestPromise = sendRequest(requestUri, requestData, "POST");

    requestPromise.then((response) => {
        if (response.status === 200) {
            console.log("Dataset created successfully");
            viewState.reset();
            imageState.reset();
        }
        else {
            console.error("Failed to create dataset");
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
        <VButton text label="Adjust" class="edit-selection" icon="pi pi-pencil" @click="handleReturnClick();" />
        <div class="element-count">
            <span class="element-count-value">{{ imageState.imageElements.length }}</span>
            <span class="element-count-label">Elements</span>
        </div>
        <VButton v-if="viewState.currentAction !== ImageAction.CreateDataset" text label="Details"
                class="quant" icon="pi pi-list" @click="quantitiesVisible = true" />
        <VButton v-else text label="Submit dataset" class="submit-dataset-button"
                icon="pi pi-check"  @click="handleSubmitClick" />
    </div>
    <VButton v-if="viewState.currentAction === ImageAction.CompareWithDataset" label="Compare with dataset"
            :class="(viewState.isWaitingForResponse ? 'inactive-button ' : '') + 'compare-button'" @click="handleCompareClick" />
    <VSidebar v-model:visible="quantitiesVisible" position="bottom" style="height: auto" class="quantities" header="Counted elements">
        <div class="quantities-label-notice">You can toggle label visibility in the settings</div>
        <div class="quantities-header">
            <div class="quantities-col">Count</div>
            <div class="quantities-col">Label<span class="rename-notice">(tap to rename)</span></div>
            <div class="quantities-col">Show boxes</div>
        </div>
        <div class="quantities-content">
            <QuantitiesEntry v-for="(quantity, index) in classifications" :key="index" :index="quantity.index" />
            <div v-if="classifications.length === 0" class="no-elements-notice">(no elements found)</div>
        </div>
    </VSidebar>
    <VDialog v-model:visible="datasetDialogVisible" modal header="Submit dataset" class="dataset-dialog"
            :dismissable-mask="true" :draggable="false">
        <p><span>{{ imageState.selectedLeaderIds.length }}</span> categories selected</p>
        <label for="dataset-name" class="dataset-label">Dataset name</label>
        <VInputText v-model="datasetName" class="dataset-name" :autofocus="true" :inputId="'dataset-name'" />
        <div class="dialog-controls">
            <VButton outlined label="Cancel" @click="datasetDialogVisible = false" />
            <VButton label="Submit" @click="submitClassificationLeaders" />
        </div>
    </VDialog>
    <VDialog v-model:visible="compareDialogVisible" modal header="Select dataset" class="compare-dialog"
            :dismissable-mask="true" :draggable="false">
        <div class="compare-dataset-list">
            <div v-for="(dataset, index) in userDatasets" :key="index" class="dataset-entry">
                <div class="dataset-entry-contents">
                    <div class="dataset-entry-name">{{ dataset.name }}</div>
                    <div class="dataset-entry-date">{{ new Date(dataset.timestamp).toISOString().split("T")[0] }}</div>
                    <div class="dataset-entry-time">{{ new Date(dataset.timestamp).toLocaleTimeString() }}</div>
                </div>
                <VButton text label="Select" class="compare-select" @click="compareWithDataset(dataset.id)" />
            </div>
        </div>
        <div class="dialog-controls">
            <VButton outlined label="Cancel" @click="compareDialogVisible = false" />
        </div>
    </VDialog>
</template>


<style scoped>
.quantities {
    overflow: hidden;
}

.quantities-header {
    display: flex;
    font-size: 0.75rem;
    font-weight: 300;
    letter-spacing: 0.3px;
    margin: 12px 0 6px 0;
    color: var(--primary-color);
    user-select: none;
}

.quantities-content {
    max-height: 60vh;
}

.quantities-col:nth-child(1) {
    flex-basis: 15%;
    text-align: center;
}

.quantities-col:nth-child(2) {
    flex-basis: 60%;
    text-indent: 10px;
}

.quantities-col:nth-child(3) {
    flex-basis: 25%;
    text-align: center;
}

.quantities-label-notice {
    font-size: 0.8rem;
    line-height: 1.1rem;
    font-weight: 300;
    letter-spacing: 0.3px;
    color: var(--text-color-secondary);
    opacity: 0.7;
    user-select: none;
    text-align: center;
}

.image-view-tool-bar {
    padding: 0;
    position: fixed;
    bottom: 0;
    height: 90px;
    align-items: stretch;
}

.image-view-tool-bar > button {
    flex-direction: column;
    padding: 12px 1rem;
    justify-content: space-between;
    flex: 1 1 0px;
}

.element-count {
    display: flex;
    flex-direction: column;
    color: var(--primary-color);
    text-align: center;
    justify-content: space-between;
    margin-top: -20px;
    background-color: var(--surface-card);
    border-top-left-radius: 30px;
    border-top-right-radius: 30px;
    padding: 10px 25px;
    -webkit-box-shadow: 0px 0px 6px 0px var(--color-shadow);
    -moz-box-shadow: 0px 0px 6px 0px var(--color-shadow);
    box-shadow: 0px 0px 6px 0px var(--color-shadow);
}

.element-count-value {
    display: block;
    font-weight: 700;
    font-size: 2.25rem;
}

.element-count-label {
    display: block;
    font-weight: 500;
}

.rename-notice,
.no-elements-notice {
    margin-left: 10px;
    color: var(--text-color-secondary);
    opacity: 0.7;
}

.no-elements-notice {
    margin: 20px 0 10px 0;
    text-align: center;
}

.dataset-dialog input {
    margin-bottom: 30px;
    width: 100%;
}

.dataset-dialog p {
    user-select: none;
    line-height: 1.8rem;
}

.dataset-dialog span {
    font-weight: 600;
    font-size: 1.4rem;
    margin-right: 2px;
}

.dataset-dialog label {
    display: inline-block;
    margin-bottom: 4px;
    margin-top: 10px;
    color: var(--text-color-secondary);
    user-select: none;
}

.dataset-dialog .dialog-controls,
.compare-dialog .dialog-controls {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

.dataset-entry-name {
    font-weight: 500;
    font-size: 1rem;
    color: var(--text-color);
}

.dataset-entry-date,
.dataset-entry-time {
    font-weight: 500;
    font-size: 0.8rem;
    color: var(--text-color-secondary);
}

.compare-button {
    position: fixed;
    bottom: 130px;
    left: 50%;
    transform: translateX(-50%);
    max-width: 240px;
    width: 100%;
}

.dataset-entry {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid var(--surface-border);
}

.compare-dialog .compare-dataset-list {
    max-height: 65vh;
    overflow-y: auto;
    margin-bottom: 18px;
}

.inactive-button {
    pointer-events: none;
    opacity: 0.5;
}
</style>

<style>
.compare-dialog {
    width: 92.5vw;
}

.quantities .p-sidebar-header {
    padding-bottom: 12px;
}

.quantities .p-sidebar-header-content {
    color: var(--primary-color);
    font-weight: 400;
    letter-spacing: 0.3px;
    user-select: none;
}

.quantity-switch .p-inputswitch-input {
    width: 40px;
    left: 50%;
    transform: translateX(-50%);
}

.quantity-switch .p-inputswitch-slider {
    width: 40px;
    margin: 0 auto;
}
</style>
