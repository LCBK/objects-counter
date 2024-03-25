<script setup lang="ts">
import { ref } from "vue";
import Button from "primevue/button";

const captureInput = ref<HTMLElement>();
const uploadInput = ref<HTMLElement>();

function onCaptureClick() {
    if (!captureInput.value) return;
    captureInput.value.click();
}

function onUploadClick() {
    if (!uploadInput.value) return;
    uploadInput.value.click();
}
</script>

<template>
    <div class="image-select">
        <Button label="Capture image" icon="pi pi-camera" @click="onCaptureClick()"></Button>
        <Button label="Upload image" icon="pi pi-upload" @click="onUploadClick()"></Button>
        <div class="image-select-inputs">
            <input type="file" name="image-capture" ref="captureInput" accept="image/*" capture="environment" />
            <input type="file" name="image-upload" ref="uploadInput" accept="image/*" />
        </div>
    </div>
</template>

<style scoped>
.image-select {
    display: flex;
    margin: 0 auto;
    flex-direction: column;
    align-items: center;
    gap: 30px;
}

.image-select Button {
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