<script setup lang="ts">
import "./ImageViewToolBar.css";
import VButton from "primevue/button";
import VDialog from "primevue/dialog";
import VSidebar from "primevue/sidebar";
import QuantitiesEntry from "../QuantitiesEntry.vue";
import MissingQuantitiesEntry from "../MissingQuantitiesEntry.vue";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { computed, ref } from "vue";
import { base64ToImageUri, parseClassificationsFromElementsResponse } from "@/utils";
import { type DatasetListItem } from "@/types/app";
import DatasetListItemComponent from "../DatasetListItem.vue";
import { compareToDataset, getDatasets, getDatasetsThumbnails } from "@/requests/datasets";


const imageState = useImageStateStore();
const viewState = useViewStateStore();

const quantitiesVisible = ref<boolean>(false);
const datasetDialogVisible = ref<boolean>(false);
const compareDialogVisible = ref<boolean>(false);
const hasCompared = ref<boolean>(false);
const userDatasets = ref<DatasetListItem[]>([]);

const classifications = computed(() => imageState.currentImage.classifications);
const missingClassifications = computed(() => {
    return Object.keys(imageState.comparisonDifference)
        .filter((key) => !classifications.value.some((c) => c.name === key));
});


function handleReturnClick() {
    viewState.setState(ViewStates.ImageEditPoints);
    viewState.showBackground = true;
    viewState.isEditingExistingResult = true;
    imageState.clearCurrentResult();
}

function handleDatasetListClick() {
    loadDatasets();
    compareDialogVisible.value = true;
}

async function loadDatasets() {
    viewState.isWaitingForResponse = true;

    await getDatasets().then((response) => {
        userDatasets.value = [];
        for (const dataset of response.filter((d) => !d.unfinished)) {
            userDatasets.value.push({
                id: dataset.id,
                name: dataset.name,
                timestamp: Date.parse(dataset.timestamp)
            } as DatasetListItem);
        }
        userDatasets.value = userDatasets.value.sort((a, b) => b.timestamp - a.timestamp);
    });

    await getDatasetsThumbnails().then((response) => {
        for (const item of response) {
            const datasetItem = userDatasets.value.find(
                (datasetItem) => datasetItem.id == item.id
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
    const imageIds = imageState.images.map((image) => image.id);

    viewState.isWaitingForResponse = true;
    compareDialogVisible.value = false;

    await compareToDataset(datasetId, imageIds).then((response) => {
        imageState.clearCurrentResult();

        parseClassificationsFromElementsResponse(response.images[0].elements);
        imageState.comparisonDifference = response.diff;

        hasCompared.value = true;
        quantitiesVisible.value = true;
        datasetDialogVisible.value = false;
        console.log(missingClassifications.value);
    }).finally(() => {
        viewState.isWaitingForResponse = false;
    });
}
</script>


<template>
    <div class="image-view-tool-bar bar">
        <div class="bar-content tool-bar-content">
            <VButton text label="Adjust" icon="pi pi-pencil" @click="handleReturnClick();" />
            <div class="element-count">
                <span class="element-count-value">{{ imageState.currentImage.elements.length }}</span>
                <span class="element-count-label">Elements</span>
            </div>
            <VButton text label="Details" icon="pi pi-list" @click="quantitiesVisible = true" :disabled="!hasCompared" />
        </div>
    </div>
    <VButton v-if="!hasCompared" :class="(viewState.isWaitingForResponse ? 'inactive-button ' : '') + 'compare-button'"
            label="Compare with dataset" @click="handleDatasetListClick" />
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
            <QuantitiesEntry v-for="(quantity, index) in classifications" :key="index" :index="quantity.index" />
            <MissingQuantitiesEntry v-for="(missing, index) in missingClassifications" :key="index" :name="missing" />
            <div v-if="classifications.length === 0" class="no-elements-notice notice">(no elements found)</div>
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

.compare-button {
    position: fixed;
    bottom: 130px;
    left: 50%;
    transform: translateX(-50%);
    max-width: 280px;
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
</style>

<style>
.compare-dialog {
    max-width: 600px;
}
</style>
