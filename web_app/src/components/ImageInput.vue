<script setup lang="ts">
import { ref } from "vue";
import VButton from "primevue/button";
import VDialog from "primevue/dialog";
import VSelectButton from "primevue/selectbutton";
import { ImageAction, useViewStateStore, ViewStates } from "@/stores/viewState";
import { isUserAgentMobile, processImageData } from "@/utils";
import { useUserStateStore } from "@/stores/userState";
import { uploadImage } from "@/requests/images";


const viewState = useViewStateStore();
const userState = useUserStateStore();

const captureInput = ref<HTMLInputElement>();
const uploadInput = ref<HTMLInputElement>();
const currentMode = ref<string>("Capture");

const isCountingDialogVisible = ref<boolean>(false);


function triggerImageInput() {
    if (!uploadInput.value || !captureInput.value) return;
    if (currentMode.value === "Capture") captureInput.value.click();
    else uploadInput.value.click();
}

function handleCountingClick() {
    isCountingDialogVisible.value = true;
}

function handleCreateDatasetClick() {
    triggerImageInput();
    viewState.currentAction = ImageAction.CreateDataset;
}

function handleCompareClick() {
    triggerImageInput();
    viewState.currentAction = ImageAction.CompareWithDataset;
}

function handleAutomaticCountingClick() {
    triggerImageInput();
    viewState.currentAction = ImageAction.AutomaticCounting;
}

function handleLeaderCountingClick() {
    triggerImageInput();
    viewState.currentAction = ImageAction.LeaderCounting;
}

async function handleImageUpload(event: Event) {
    const imageFile = (event.target as HTMLInputElement)!.files?.[0];
    if (imageFile === undefined) return;

    viewState.setState(ViewStates.Uploading);

    await uploadImage(imageFile).then(imageId => {
        processImageData(imageFile, imageId);
        viewState.setState(ViewStates.ImageEditPoints);
    }).catch(() => {
        viewState.setState(ViewStates.MainView);
    });
}
</script>


<template>
    <div class="image-select">
        <VButton class="wide-button" label="Count elements" icon="pi pi-box" @click="handleCountingClick" />
        <p v-if="!userState.isLoggedIn" class="login-notice notice">Log in to access functions below</p>
        <VButton class="wide-button" label="Create dataset" icon="pi pi-images"
                :disabled="!userState.isLoggedIn" @click="handleCreateDatasetClick" />
        <VButton class="wide-button" label="Compare elements" icon="pi pi-arrow-right-arrow-left"
                :disabled="!userState.isLoggedIn" @click="handleCompareClick" />
        <VSelectButton v-if="isUserAgentMobile()" class="mode-select" v-model="currentMode"
                :options="['Capture', 'Upload']" :allow-empty="false" />
    </div>
    <div class="image-inputs">
        <input type="file" name="image-capture" ref="captureInput"
                accept="image/*" capture="environment" @change.stop.prevent="handleImageUpload($event)" />
        <input type="file" name="image-upload" ref="uploadInput"
                accept="image/*" @change.stop.prevent="handleImageUpload($event)" />
    </div>
    <VDialog v-model:visible="isCountingDialogVisible" modal header="Choose method"
            class="counting-dialog input-dialog" :dismissable-mask="true" :draggable="false">
        <VButton label="Automatic counting" icon="pi pi-sync" @click="handleAutomaticCountingClick" />
        <VButton label="Leader selection" icon="pi pi-pencil" @click="handleLeaderCountingClick" />
    </VDialog>
</template>


<style scoped>
.image-select {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 30px;
}

.login-notice {
    margin-bottom: -15px;
    user-select: none;
}
</style>

<style>
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

@media screen and (min-width: 340px) {
    .image-select .p-button-label {
        font-size: 1.2rem;
    }
}
</style>
