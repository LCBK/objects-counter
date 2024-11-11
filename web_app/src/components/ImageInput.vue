<script setup lang="ts">
import { ref } from "vue";
import VButton from "primevue/button";
import VSelectButton from "primevue/selectbutton";
import { useImageStateStore } from "@/stores/imageState";
import { ImageAction, useViewStateStore, ViewStates } from "@/stores/viewState";
import { sendRequest } from "@/utils";
import { config, endpoints } from "@/config";
import { useUserStateStore } from "@/stores/userState";


const imageState = useImageStateStore();
const viewState = useViewStateStore();
const userState = useUserStateStore();

const captureInput = ref<HTMLInputElement>();
const uploadInput = ref<HTMLInputElement>();
const currentMode = ref<string>("Capture");


function triggerImageInput() : void {
    if (!uploadInput.value || !captureInput.value) return;
    if (currentMode.value === "Capture") captureInput.value.click();
    else uploadInput.value.click();
}

function handleCountingClick() : void {
    triggerImageInput();
    viewState.currentAction = ImageAction.SimpleCounting;
}

function handleCreateDatasetClick() : void {
    triggerImageInput();
    viewState.currentAction = ImageAction.CreateDataset;
}

function handleCompareClick() : void {
    triggerImageInput();
    viewState.currentAction = ImageAction.CompareWithDataset;
}

function handleImageUpload(event: Event) : void {
    const imageFile = (event.target as HTMLInputElement)!.files?.[0];
    if (imageFile !== undefined) {
        // Set image URL to display it later on
        const url = window.URL.createObjectURL(imageFile);
        imageState.url = url;

        // Get image dimensions
        const img = new Image;
        img.src = url;
        img.onload = () => {
            imageState.width = img.width;
            imageState.height = img.height;
        };

        // Upload image to server
        const requestUri = config.serverUri + endpoints.uploadImage;
        const requestData = new FormData();
        requestData.append("image", imageFile);
        const responsePromise = sendRequest(requestUri, requestData, "POST", "multipart/form-data");

        viewState.isImageUploading = true;
        viewState.setState(ViewStates.Uploading);

        responsePromise.then((response) => {
            viewState.isImageUploading = false;
            viewState.isImageUploaded = true;

            if (response.status === 201) {
                imageState.imageId = response.data;
                viewState.setState(ViewStates.ImageEditPoints);
            }
            else {
                console.error("Failed to upload image");
                viewState.setState(ViewStates.MainView);
            }
        });
    }
}
</script>


<template>
    <div class="image-select">
        <VButton class="wide-button" label="Count elements" icon="pi pi-box" @click="handleCountingClick()" />
        <p v-if="!userState.isLoggedIn" class="login-notice notice">Log in to access functions below</p>
        <VButton class="wide-button" label="Create dataset" icon="pi pi-images"
                :disabled="!userState.isLoggedIn" @click="handleCreateDatasetClick()" />
        <VButton class="wide-button" label="Compare quantity" icon="pi pi-arrow-right-arrow-left"
                :disabled="!userState.isLoggedIn" @click="handleCompareClick()" />
        <VSelectButton class="mode-select" v-model="currentMode" :options="['Capture', 'Upload']" :allow-empty="false" />
    </div>
    <div class="image-select-inputs">
        <input type="file" name="image-capture" ref="captureInput"
            accept="image/*" capture="environment" @change.stop.prevent="handleImageUpload($event)" />
        <input type="file" name="image-upload" ref="uploadInput"
            accept="image/*" @change.stop.prevent="handleImageUpload($event)" />
    </div>
</template>


<style scoped>
.image-select {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 30px;
}

.image-select-inputs input {
    width: 0px;
    height: 0px;
    overflow: hidden;
}

.login-notice {
    margin-bottom: -15px;
    user-select: none;
}
</style>

<style>
.image-select .p-button-icon {
    font-size: 1.25rem;
}

.mode-select .p-button {
    border: none;
}

.mode-select .p-button span {
    font-weight: 600;
}

.mode-select .p-button:active {
    background-color: unset;
    color: unset;
}

.mode-select .p-button.p-highlight::before {
    background-color: var(--primary-color);
}

.mode-select .p-button.p-highlight {
    color: var(--primary-color-text);
}

.dark .mode-select .p-button {
    background-color: #0a0a0a;
}
</style>
