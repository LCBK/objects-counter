<script setup lang="ts">
import "./ImageViewToolBar.css";
import VButton from "primevue/button";
import { useImageStateStore } from "@/stores/imageState";
import { ImageAction, useViewStateStore, ViewStates } from "@/stores/viewState";
import { parseElementsToImage } from "@/utils";
import { addImageToDataset, createDataset } from "@/requests/datasets";
import { computed } from "vue";


const imageState = useImageStateStore();
const viewState = useViewStateStore();

const submitDisabled = computed(() => {
    return imageState.currentImage.selectedLeaderIds.length === 0
        && viewState.isAddingMoreImages === false;
});


function handleReturnClick() {
    imageState.clearCurrentResult();
    imageState.currentImage.selectedLeaderIds = [];

    viewState.showBackground = true;
    viewState.isEditingExistingResult = true;
    viewState.setState(ViewStates.ImageViewEditPoints);
}

function handleSubmitLeadersClick() {
    submitClassificationLeaders();
}

async function submitClassificationLeaders() {
    viewState.isWaitingForResponse = true;

    if (!viewState.isAddingMoreImages) {
        await createDataset(`temporary no. ${imageState.currentImage.id}`, true).then((response) => {
            imageState.datasetId = parseInt(response);
        }).catch(() => {
            viewState.isWaitingForResponse = false;
            return;
        });
    }

    const classifications = imageState.currentImage.selectedLeaderIds.map(id => {
        return {
            name: viewState.lastAssignedLeaderNumber++,
            leader_id: id
        }
    });

    await addImageToDataset(imageState.datasetId, imageState.currentImage.id, classifications).then(response => {
        imageState.clearCurrentResult();

        const currentImage = response.images.find(image => image.id === imageState.currentImage.id);
        if (currentImage !== undefined) {
            parseElementsToImage(imageState.currentImage.id, currentImage.elements);

            if (viewState.currentAction === ImageAction.CreateDataset) {
                viewState.setState(ViewStates.ImageViewConfirmDataset);
            }
        }
    }).finally(() => {
        viewState.isWaitingForResponse = false;
    });
}
</script>


<template>
    <div class="image-view-tool-bar bar">
        <div class="bar-content tool-bar-content">
            <VButton text label="Adjust background" icon="pi pi-pencil" @click="handleReturnClick" />
            <div class="element-count">
                <span class="element-count-value">{{ imageState.currentImage.elements.length }}</span>
                <span class="element-count-label">Elements</span>
            </div>
            <VButton text label="Submit selection" icon="pi pi-check"
                    @click="handleSubmitLeadersClick" :disabled="submitDisabled" />
        </div>
    </div>
</template>
