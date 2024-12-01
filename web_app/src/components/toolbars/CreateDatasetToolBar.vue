<script setup lang="ts">
import "./ImageViewToolBar.css";
import VButton from "primevue/button";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { parseClassificationsFromElementsResponse } from "@/utils";
import { sendLeaders } from "@/requests/images";
import { addImageToDataset, createDataset } from "@/requests/datasets";


const imageState = useImageStateStore();
const viewState = useViewStateStore();


function handleReturnClick() {
    imageState.clearResult();
    imageState.selectedLeaderIds = [];

    viewState.showBackground = true;
    viewState.isEditingExistingResult = true;
    viewState.setState(ViewStates.ImageEditPoints);
}

function handleSubmitLeadersClick() {
    submitClassificationLeaders();
}

async function submitClassificationLeaders() {
    viewState.isWaitingForResponse = true;

    await sendLeaders(imageState.currentImage.id, imageState.selectedLeaderIds).catch(() => {
        viewState.isWaitingForResponse = false;
        return;
    });

    if (!viewState.isAddingMoreImages) {
        await createDataset(`temporary no. ${imageState.currentImage.id}`, true).then((response) => {
            imageState.datasetId = parseInt(response);
        }).catch(() => {
            viewState.isWaitingForResponse = false;
            return;
        });
    }

    const classifications = imageState.selectedLeaderIds.map(id => {
        return {
            name: viewState.lastAssignedLeaderNumber++,
            leader_id: id
        }
    });

    await addImageToDataset(imageState.datasetId, imageState.currentImage.id, classifications).then((response) => {
        imageState.clearResult();

        const currentImage = response.images.find((image) => image.id === imageState.currentImage.id);
        if (currentImage !== undefined) {
            parseClassificationsFromElementsResponse(currentImage.elements);
            viewState.setState(ViewStates.ImageViewConfirmDataset);
        }
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
            <VButton text label="Submit leaders" icon="pi pi-check"
                    @click="handleSubmitLeadersClick" :disabled="imageState.selectedLeaderIds.length === 0" />
        </div>
    </div>
</template>
