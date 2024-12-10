<script setup lang="ts">
import "./ImageViewToolBar.css";
import VButton from "primevue/button";
import VDialog from "primevue/dialog";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { ref } from "vue";
import {
    base64ToImageUri,
    isUserAgentMobile,
    parseMultipleClassificationsFromResponse,
    processImageData
} from "@/utils";
import { type DatasetListItem } from "@/types/app";
import DatasetListItemComponent from "../DatasetListItem.vue";
import { getDatasets, getDatasetsThumbnails } from "@/requests/datasets";
import { compareToDataset } from "@/requests/comparisons";
import ImageNavigationOverlay from "../ImageNavigationOverlay.vue";
import { uploadImage } from "@/requests/images";


const imageState = useImageStateStore();
const viewState = useViewStateStore();

const uploadInput = ref<HTMLInputElement>();
const captureInput = ref<HTMLInputElement>();

const datasetDialogVisible = ref<boolean>(false);
const compareDialogVisible = ref<boolean>(false);
const addImageDialogVisible = ref<boolean>(false);
const userDatasets = ref<DatasetListItem[]>([]);


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

        imageState.comparisonId = response.id;
        imageState.comparisonDifference = response.diff;
        imageState.comparisonDatasetName = response.dataset.name;

        datasetDialogVisible.value = false;
        viewState.setState(ViewStates.ImageViewComparisonResult);
    }).finally(() => {
        viewState.isWaitingForResponse = false;
    });
}

async function handleImageUpload(event: Event) {
    const imageFile = (event.target as HTMLInputElement)!.files?.[0];
    if (imageFile === undefined) return;

    viewState.setState(ViewStates.Uploading);

    await uploadImage(imageFile).then(imageId => {
        processImageData(imageFile, imageId);

        // The store state is before the upload, so this length is one less than the actual one
        imageState.currentImageIndex = imageState.images.length;

        viewState.isAddingMoreImages = true;
        viewState.setState(ViewStates.ImageEditPoints);
    }).catch(() => {
        viewState.setState(ViewStates.MainView);
    });
}

function handleCaptureClick() {
    captureInput.value!.click();
}

function handleUploadClick() {
    uploadInput.value!.click();
}

function handleAddImage() {
    if (isUserAgentMobile()) {
        addImageDialogVisible.value = true;
    } else {
        uploadInput.value!.click();
    }
}
</script>


<template>
    <div class="image-view-tool-bar bar">
        <div class="bar-content tool-bar-content">
            <VButton text label="Adjust" icon="pi pi-pencil" @click="handleReturnClick();" />
            <VButton text label="Add next image" icon="pi pi-plus" @click="handleAddImage" />
            <VButton text label="Select comparison" icon="pi pi-chart-bar" @click="handleDatasetListClick" />
        </div>
    </div>
    <ImageNavigationOverlay v-if="imageState.images.length > 1" />
    <VDialog v-model:visible="compareDialogVisible" modal header="Select dataset" class="compare-dialog"
            :dismissable-mask="true" :draggable="false">
        <div class="compare-dataset-list">
            <div v-for="(dataset, index) in userDatasets" :key="index">
                <DatasetListItemComponent v-bind="dataset" @compare-click="handleCompareClick" />
            </div>
        </div>
    </VDialog>
    <VDialog v-model:visible="addImageDialogVisible" modal header="Choose source"
            class="image-dialog input-dialog" :dismissable-mask="true" :draggable="false">
        <VButton label="Capture image" icon="pi pi-camera" @click="handleCaptureClick" />
        <VButton label="Upload image" icon="pi pi-upload" @click="handleUploadClick" />
    </VDialog>
    <div class="image-inputs">
        <input type="file" name="image-capture" ref="captureInput"
            accept="image/*" capture="environment" @change.stop.prevent="handleImageUpload($event)" />
        <input type="file" name="image-upload" ref="uploadInput"
            accept="image/*" @change.stop.prevent="handleImageUpload($event)" />
    </div>
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

.image-inputs input {
    width: 0px;
    height: 0px;
    overflow: hidden;
}
</style>

<style>
.compare-dialog {
    max-width: 600px;
}
</style>
