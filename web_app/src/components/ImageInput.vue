<script setup lang="ts">
import { ref } from "vue";
import VButton from "primevue/button";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { sendRequest } from "@/utils";
import { config, endpoints } from "@/config";


const imageState = useImageStateStore();
const viewState = useViewStateStore();
const captureInput = ref<HTMLInputElement>();
const uploadInput = ref<HTMLInputElement>();


function onCaptureClick() : void {
    if (!captureInput.value) return;
    captureInput.value.click();
}

function onUploadClick() : void {
    if (!uploadInput.value) return;
    uploadInput.value.click();
}

function onImageUpload(event: Event) : void {
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
        viewState.isImageUploading = true;
        viewState.setState(ViewStates.Uploading);
        const responsePromise = sendRequest(requestUri, requestData, "POST", "multipart/form-data");

        // Handle server response
        responsePromise.then((response) => {
            viewState.isImageUploading = false;
            viewState.isImageUploaded = true;
            viewState.setState(ViewStates.ImageEditPoints);
            imageState.imageId = response.data;
        });
    }
}
</script>


<template>
    <div class="image-select">
        <VButton class="wide-button" label="Capture image" icon="pi pi-camera" @click="onCaptureClick()"></VButton>
        <VButton class="wide-button" label="Upload image" icon="pi pi-upload" @click="onUploadClick()"></VButton>
    </div>
    <div class="image-select-inputs">
        <input type="file" name="image-capture" ref="captureInput"
            accept="image/*" capture="environment" @change.stop.prevent="onImageUpload($event)" />
        <input type="file" name="image-upload" ref="uploadInput"
            accept="image/*" @change.stop.prevent="onImageUpload($event)" />
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
</style>

<style>
.image-select .p-button-icon {
    font-size: 1.25rem;
    font-weight: 600;
}
</style>
