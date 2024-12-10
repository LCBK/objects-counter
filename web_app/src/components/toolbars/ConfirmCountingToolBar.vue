<script setup lang="ts">
import "./ImageViewToolBar.css";
import VButton from "primevue/button";
import VDialog from "primevue/dialog";
import ImageNavigationOverlay from "../ImageNavigationOverlay.vue";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { ref } from "vue";
import { uploadImage } from "@/requests/images";
import { isUserAgentMobile, parseMultipleClassificationsFromResponse, processImageData } from "@/utils";
import { createResult } from "@/requests/results";


const imageState = useImageStateStore();
const viewState = useViewStateStore();

const uploadInput = ref<HTMLInputElement>();
const captureInput = ref<HTMLInputElement>();

const addImageDialogVisible = ref<boolean>(false);


function handleReturnClick() {
    viewState.setState(ViewStates.ImageEditPoints);
    viewState.showBackground = true;
    imageState.clearAllResults();
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

async function handleConfirmCountingClick() {
    viewState.isWaitingForResponse = true;

    const imageIds = imageState.images.map(image => image.id);

    await createResult(imageIds).then(response => {
        imageState.clearAllResults();

        parseMultipleClassificationsFromResponse(response.images);
        imageState.resultId = response.id;

        viewState.setState(ViewStates.ImageViewCountingResult);
    }).finally(() => {
        viewState.isWaitingForResponse = false;
    });
}
</script>


<template>
    <div class="image-view-tool-bar bar">
        <div class="bar-content tool-bar-content">
            <VButton text label="Adjust background" icon="pi pi-pencil" @click="handleReturnClick" />
            <VButton text label="Add next image" icon="pi pi-plus" @click="handleAddImage" />
            <VButton text label="Confirm" icon="pi pi-check" @click="handleConfirmCountingClick" />
        </div>
    </div>
    <ImageNavigationOverlay v-if="imageState.images.length > 1" />
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
