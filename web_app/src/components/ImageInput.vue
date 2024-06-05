<script setup lang="ts">
import { ref } from "vue";
import VButton from "primevue/button";
import { useImageStateStore } from "@/stores/imageState";
import { sendRequest } from "@/utils";
import { config, endpoints } from "@/config";


const imageState = useImageStateStore();
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

        // Upload image to server
        const requestUri = config.serverUri + endpoints.processImage;
        const requestData = new FormData();
        requestData.append("image", imageFile);

        imageState.isUploading = true;
        const responsePromise = sendRequest(requestUri, requestData, "POST");
        responsePromise.then((response) => {
            // todo: handle response codes
            imageState.isUploading = false;
            imageState.isUploaded = true;
            imageState.result = response.data;
        });
    }
}
</script>


<template>
    <div class="image-select">
        <VButton label="Capture image" icon="pi pi-camera" @click="onCaptureClick()"></VButton>
        <VButton label="Upload image" icon="pi pi-upload" @click="onUploadClick()"></VButton>
    </div>
    <div class="image-select-inputs">
        <input type="file" name="image-capture" ref="captureInput"
            accept="image/*" capture="environment" @change.prevent="onImageUpload($event)" />
        <input type="file" name="image-upload" ref="uploadInput"
            accept="image/*" @change.prevent="onImageUpload($event)" />
    </div>
</template>


<style scoped>
.image-select {
    display: flex;
    margin: auto 0;
    flex-direction: column;
    align-items: center;
    gap: 30px;
}

.image-select button {
    width: 90%;
    max-width: 240px;
    height: 50px;
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
}
</style>
