<script setup lang="ts">
import "./ImageViewToolBar.css";
import VButton from "primevue/button";
import VDialog from "primevue/dialog";
import VSidebar from "primevue/sidebar";
import VInputText from "primevue/inputtext";
import QuantitiesEntry from "../QuantitiesEntry.vue";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { computed, ref, watch } from "vue";
import {
    formatClassificationName,
    getClassificationBoxColor,
    isUserAgentMobile,
    processImageData
} from "@/utils";
import InfoPopup from "../InfoPopup.vue";
import { adjustClassifications, renameDataset } from "@/requests/datasets";
import { uploadImage } from "@/requests/images";
import ImageNavigationOverlay from "../ImageNavigationOverlay.vue";


const imageState = useImageStateStore();
const viewState = useViewStateStore();

const captureInput = ref<HTMLInputElement>();
const uploadInput = ref<HTMLInputElement>();

const quantitiesVisible = ref<boolean>(false);
const createDatasetDialogVisible = ref<boolean>(false);
const addImageDialogVisible = ref<boolean>(false);

const datasetName = ref<string>("");
const popupText = ref<string>("");
const popupHeader = ref<string>("");
const popupVisible = ref<boolean>(false);
const isSuccessfullyCreated = ref<boolean>(false);

const assignedClassificationName = computed(() => {
    return formatClassificationName(viewState.currentlyAssignedClassificationName);
});

const assignedBoxColor = computed(() => {
    return getClassificationBoxColor(viewState.currentlyAssignedClassificationName);
});


// Close quantities sidebar when user starts to assign classifications
watch(() => viewState.isSelectingAssignment, newValue => {
    if (!newValue) {
        quantitiesVisible.value = false;
    }
});


function handleAddImage() {
    if (isUserAgentMobile()) {
        addImageDialogVisible.value = true;
    } else {
        uploadInput.value!.click();
    }
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

        viewState.setState(ViewStates.ImageViewEditPoints);
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

async function submitDataset() {
    imageState.images.forEach(image => {
        const classifications = imageState.classifications.map(c => {
            return {
                name: c.name,
                elements: image.elements
                    .filter((el) => el.classificationName === c.name)
                    .map((el) => el.id)
            };
        });

        adjustClassifications(imageState.datasetId, image.id, classifications);
    });

    await renameDataset(imageState.datasetId, datasetName.value).then(() => {
        popupText.value = "Dataset submitted successfully";
        popupHeader.value = "Success";
        popupVisible.value = true;
        isSuccessfullyCreated.value = true;
    }).catch(() => {
        popupText.value = "Failed to submit dataset";
        popupHeader.value = "Error";
        popupVisible.value = true;
    });
}

function handleCreatedDataset() {
    window.setTimeout(() => {
        if (isSuccessfullyCreated.value) {
            viewState.reset();
            imageState.reset();
        }
    }, 500);
}
</script>


<template>
    <div class="image-view-tool-bar bar">
        <div class="bar-content tool-bar-content">
            <VButton text label="Adjust categories" icon="pi pi-list" @click="quantitiesVisible = true" />
            <VButton text label="Add next image" icon="pi pi-plus" @click="handleAddImage" />
            <VButton text label="Create dataset" icon="pi pi-check" @click="createDatasetDialogVisible = true" />
        </div>
    </div>
    <ImageNavigationOverlay v-if="imageState.images.length > 1" />
    <Transition name="fade">
        <div v-if="viewState.isAssigningClassifications" class="assignment-notice">
            <VButton text icon="pi pi-times" @click="viewState.isAssigningClassifications = false" />
            <div>
                <div class="assignment-notice-label">Currently assigning</div>
                <div class="assignment-notice-value"><span>{{ assignedClassificationName }}</span></div>
            </div>
        </div>
    </Transition>
    <VSidebar v-model:visible="quantitiesVisible" position="bottom" style="height: auto"
            class="quantities" header="Counted elements" @hide="viewState.isSelectingAssignment = false">
        <VButton text label="Assign categories" icon="pi pi-pencil" class="change-categories"
                @click="viewState.isSelectingAssignment = true" />
        <div class="quantities-label-notice notice">You can toggle label visibility in the settings</div>
        <div class="quantities-header">
            <div class="quantities-col">Count</div>
            <div class="quantities-col">Label<span class="rename-notice notice">(tap to rename)</span></div>
            <div v-if="!viewState.isSelectingAssignment" class="quantities-col">Show boxes</div>
        </div>
        <div class="quantities-content">
            <QuantitiesEntry v-for="(classification, index) in imageState.classifications"
                    :key="index" :name="classification.name" />
            <div v-if="imageState.classifications.length === 0" class="no-elements-notice notice">
                (no elements found)
            </div>
        </div>
    </VSidebar>
    <VDialog v-model:visible="addImageDialogVisible" modal header="Choose source"
            class="image-dialog input-dialog" :dismissable-mask="true" :draggable="false">
        <VButton label="Capture image" icon="pi pi-camera" @click="handleCaptureClick" />
        <VButton label="Upload image" icon="pi pi-upload" @click="handleUploadClick" />
    </VDialog>
    <VDialog v-model:visible="createDatasetDialogVisible" modal header="Submit dataset"
            class="dataset-dialog input-dialog" :dismissable-mask="true" :draggable="false">
        <label for="dataset-name" class="dataset-label">Dataset name</label>
        <VInputText v-model="datasetName" class="dataset-name" :autofocus="true" :inputId="'dataset-name'"
                placeholder="My board game" />
        <div class="dialog-controls">
            <VButton outlined label="Cancel" @click="createDatasetDialogVisible = false" />
            <VButton label="Submit" @click="submitDataset" />
        </div>
    </VDialog>
    <div class="image-inputs">
        <input type="file" name="image-capture" ref="captureInput"
                accept="image/*" capture="environment" @change.stop.prevent="handleImageUpload($event)" />
        <input type="file" name="image-upload" ref="uploadInput"
                accept="image/*" @change.stop.prevent="handleImageUpload($event)" />
    </div>
    <InfoPopup v-model="popupVisible" :text="popupText" :header="popupHeader"
            @close="handleCreatedDataset" :timeout="2500" />
</template>


<style scoped>
.change-categories {
    margin: 5px auto 10px auto;
    display: block;
    padding: 6px 12px;
    text-decoration: underline;
}

.assignment-notice {
    display: flex;
    position: absolute;
    bottom: 150px;
    left: 10px;
}

.assignment-notice-label {
    font-size: 0.8rem;
    color: var(--text-color-secondary);
    line-height: 1.1rem;
    color: #aaa;
    mix-blend-mode: difference;
}

.assignment-notice-value > span {
    color: #f0f0f0;
    mix-blend-mode: difference;
}

.assignment-notice-value::before {
    content: "";
    width: 10px;
    height: 10px;
    background-color: v-bind(assignedBoxColor);
    display: inline-block;
    margin-right: 6px;
}
@media screen and (min-width: 340px) {
    .assignment-notice {
        bottom: 160px;
    }
}

@media screen and (min-width: 400px) {
    .assignment-notice-label {
        font-size: 1rem;
    }

    .assignment-notice-value::before {
        width: 12px;
        height: 12px;
    }

    .assignment-notice-value {
        font-size: 1.2rem;
    }
}
</style>

<style>
.quantities .p-sidebar-header {
    padding-bottom: 6px;
}

.change-categories .pi {
    margin-right: 8px;
}

@media screen and (min-width: 400px) {
    .change-categories .p-button-label {
        font-size: 1.1rem;
    }
}
</style>
