<script setup lang="ts">
import "./ImageViewToolBar.css";
import VButton from "primevue/button";
import VDialog from "primevue/dialog";
import VSidebar from "primevue/sidebar";
import QuantitiesEntry from "../QuantitiesEntry.vue";
import MissingQuantitiesEntry from "../MissingQuantitiesEntry.vue";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore } from "@/stores/viewState";
import { computed, ref } from "vue";
import { base64ToImageUri, parseMultipleClassificationsFromResponse } from "@/utils";
import { type DatasetListItem } from "@/types/app";
import DatasetListItemComponent from "../DatasetListItem.vue";
import { getDatasets, getDatasetsThumbnails } from "@/requests/datasets";
import { compareToDataset } from "@/requests/comparisons";
import ImageNavigationOverlay from "../ImageNavigationOverlay.vue";


const imageState = useImageStateStore();
const viewState = useViewStateStore();

const quantitiesVisible = ref<boolean>(false);
const datasetDialogVisible = ref<boolean>(false);
const compareDialogVisible = ref<boolean>(false);
const userDatasets = ref<DatasetListItem[]>([]);

const missingClassifications = computed(() => {
    return Object.keys(imageState.comparisonDifference)
        .filter(key => !imageState.classifications.some(c => c.name === key));
});


function handleDatasetListClick() {
    loadDatasets();
    compareDialogVisible.value = true;
}

async function loadDatasets() {
    viewState.isWaitingForResponse = true;

    await getDatasets().then(response => {
        userDatasets.value = [];
        for (const dataset of response.filter(d => !d.unfinished)) {
            userDatasets.value.push({
                id: dataset.id,
                name: dataset.name,
                timestamp: Date.parse(dataset.timestamp)
            } as DatasetListItem);
        }
        userDatasets.value = userDatasets.value.sort((a, b) => b.timestamp - a.timestamp);
    });

    await getDatasetsThumbnails().then(response => {
        for (const item of response) {
            const datasetItem = userDatasets.value.find(
                datasetItem => datasetItem.id == item.id
            ) as DatasetListItem;

            if (datasetItem) {
                datasetItem.thumbnailUri = base64ToImageUri(item.thumbnail);
            }
        }
    }).finally(() => {
        viewState.isWaitingForResponse = false;
    });
}

async function handleCompareClick(datasetId: number) {
    const imageIds = imageState.images.map(image => image.id);

    viewState.isWaitingForResponse = true;
    compareDialogVisible.value = false;

    await compareToDataset(datasetId, imageIds).then(response => {
        imageState.clearCurrentResult();

        parseMultipleClassificationsFromResponse(response.images);
        imageState.comparisonDifference = response.diff;

        quantitiesVisible.value = true;
        datasetDialogVisible.value = false;
    }).finally(() => {
        viewState.isWaitingForResponse = false;
    });
}
</script>


<template>
    <div class="image-view-tool-bar bar">
        <div class="bar-content tool-bar-content">
            <VButton text label="Details" icon="pi pi-list" @click="quantitiesVisible = true" />
            <VButton text label="Change comparison" icon="pi pi-chart-bar" @click="handleDatasetListClick" />
        </div>
    </div>
    <div class="dataset-name">
        <div class="dataset-name-label">Comparing with:</div>
        <div class="dataset-name-value">{{ imageState.comparisonDatasetName }}</div>
    </div>
    <ImageNavigationOverlay v-if="imageState.images.length > 1" />
    <VSidebar v-model:visible="quantitiesVisible" position="bottom" style="height: auto"
            class="quantities" header="Counted elements">
        <div class="difference-notice">
            <span v-if="Object.values(imageState.comparisonDifference).every(x => x === 0)" class="match">
                All elements match
            </span>
            <span v-else class="mismatch">Elements mismatch</span>
        </div>
        <div class="quantities-label-notice notice">You can toggle label visibility in the settings</div>
        <div class="quantities-header">
            <div class="quantities-col quantities-count-diff">Count</div>
            <div class="quantities-col">Label<span class="rename-notice notice">(tap to rename)</span></div>
            <div class="quantities-col">Show boxes</div>
        </div>
        <div class="quantities-content">
            <QuantitiesEntry v-for="(classification, index) in imageState.classifications"
                    :key="index" :name="classification.name" />
            <MissingQuantitiesEntry v-for="(missing, index) in missingClassifications" :key="index" :name="missing" />
            <div v-if="imageState.classifications.length === 0" class="no-elements-notice notice">
                (no elements found)
            </div>
        </div>
    </VSidebar>
    <VDialog v-model:visible="compareDialogVisible" modal header="Select dataset" class="compare-dialog"
            :dismissable-mask="true" :draggable="false">
        <div class="compare-dataset-list">
            <div v-for="(dataset, index) in userDatasets" :key="index">
                <DatasetListItemComponent v-bind="dataset" @compare-click="handleCompareClick" />
            </div>
        </div>
    </VDialog>
</template>


<style scoped>
.compare-dialog .dialog-controls {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
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

.dataset-name {
    display: flex;
    flex-direction: column;
    position: absolute;
    top: 70px;
    left: 12px;
    mix-blend-mode: difference;
}

.dataset-name-label {
    font-size: 0.85rem;
    line-height: 1.2rem;
    color: #aaa;
}

.dataset-name-value {
    font-size: 1.2rem;
    font-weight: 500;
    line-height: 1.6rem;
    color: #f0f0f0;
}

.difference-notice {
    display: flex;
    justify-content: center;
    margin-bottom: 8px;
    font-weight: 500;
    font-size: 1.2rem;
    user-select: none;
}

.mismatch {
    color: var(--color-error);
}

.match {
    color: var(--color-success);
}

.quantities-count-diff {
    flex-basis: 20%;
}

.quantities-col:nth-child(1) {
    flex-basis: 20%;
}

.quantities-col:nth-child(2) {
    flex-basis: 55%;
}

@media screen and (min-width: 340px) {
    .dataset-name {
        top: 80px;
    }
}
</style>

<style>
.compare-dialog {
    max-width: 600px;
}

.quantity-count {
    flex-basis: 20% !important;
}

.quantity-classification {
    flex-basis: 55% !important;
}
</style>
