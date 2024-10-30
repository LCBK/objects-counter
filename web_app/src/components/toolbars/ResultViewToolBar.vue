<script setup lang="ts">
import VButton from "primevue/button";
import VSidebar from "primevue/sidebar";
import VInputText from "primevue/inputtext";
import QuantitiesEntry from "../QuantitiesEntry.vue";
import { useImageStateStore } from "@/stores/imageState";
import { ImageAction, useViewStateStore, ViewStates } from "@/stores/viewState";
import { computed, ref } from "vue";
import { config, endpoints } from "@/config";
import { parseClassificationsFromResponse, sendRequest } from "@/utils";


const imageState = useImageStateStore();
const viewState = useViewStateStore();

const visible = ref<boolean>();
const comparisonDatasetId = ref<string>();      // temporary
const classifications = computed(() => imageState.objectClassifications);


function handleReturnClick() {
    viewState.setState(ViewStates.ImageEditPoints);
    viewState.showBackground = true;
    viewState.isEditingExistingResult = true;
    imageState.clearResult();
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
        name: "Test dataset " + imageState.imageId,
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

function compareToDataset() {
    // TODO: temporary, rework
    const requestUri = config.serverUri + endpoints.compareToDataset
            .replace("{result_id}", imageState.resultId.toString())
            .replace("{dataset_id}", comparisonDatasetId.value!.toString());
    const requestPromise = sendRequest(requestUri, null, "GET");
    requestPromise.then((response) => {
        if (response.status === 200) {
            console.log("Comparison successful");
            imageState.objectClassifications = [];
            imageState.imageElements = [];
            parseClassificationsFromResponse(response.data.classifications);
        }
        else {
            console.error("Comparison failed");
        }
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
                class="quant" icon="pi pi-list" @click="visible = true" />
        <VButton v-else text label="Submit dataset" class="submit-dataset-button"
                icon="pi pi-check"  @click="submitClassificationLeaders" />
    </div>
    <!-- TEMPORARY SOLUTION -->
    <!-- TODO: implement as clicking on bounding boxes of leaders -->
    <!-- <div class="leader-input" v-if="viewState.currentAction === ImageAction.CreateDataset"
            style="position: absolute; bottom: 120px; left: 50%; transform: translateX(-50%);">
        <p style="text-align: center; margin-bottom: 10px; color: var(--primary-color);">Leader IDs separated with spaces</p>
        <VInputText v-model="leaderIds" />
        <VButton text label="Submit" @click="submitClassificationLeaders"
                style="left: 50%; transform: translateX(-50%);" />
    </div> -->
    <div class="compare-results" v-if="viewState.currentAction === ImageAction.Compare"
            style="position: absolute; bottom: 120px; left: 50%; transform: translateX(-50%);">
        <p style="text-align: center; margin-bottom: 10px; font-size: 13px; color: var(--primary-color);">
            Enter dataset ID to compare to (read from earlier console.log, turn on persistent logs if troublesome)
        </p>
        <VInputText v-model="comparisonDatasetId" />
        <VButton text label="Submit" @click="compareToDataset"
                style="left: 50%; transform: translateX(-50%);" />
    </div>
    <!-- ================== -->
    <VSidebar v-model:visible="visible" position="bottom" style="height: auto" class="quantities" header="Counted elements">
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
</style>

<style>
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
