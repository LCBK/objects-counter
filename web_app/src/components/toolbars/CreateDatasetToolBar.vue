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
    viewState.setState(ViewStates.ImageEditPoints);
    viewState.showBackground = true;
    viewState.isEditingExistingResult = true;
    imageState.clearResult();
    imageState.selectedLeaderIds = [];
}

function handleSubmitLeadersClick() {
    submitClassificationLeaders();
}

async function submitClassificationLeaders() {
    viewState.isWaitingForResponse = true;

    await sendLeaders(imageState.imageId, imageState.selectedLeaderIds).then(() => {
        createDataset("temporary no. " + imageState.imageId).then((response) => {
            imageState.datasetId = parseInt(response);

            const classifications = imageState.selectedLeaderIds.map((id: any, index: number) => {
                return {
                    name: index,
                    leader_id: id
                }
            });

            addImageToDataset(imageState.datasetId, imageState.imageId, classifications).then((response) => {
                imageState.clearResult();
                parseClassificationsFromElementsResponse(response.images[0].elements);
                viewState.setState(ViewStates.ImageViewConfirmDataset);
                viewState.isWaitingForResponse = false;
            });
        });
    });
}
</script>


<template>
    <div class="image-view-tool-bar bar">
        <div class="bar-content tool-bar-content">
            <VButton text label="Adjust" icon="pi pi-pencil" @click="handleReturnClick();" />
            <div class="element-count">
                <span class="element-count-value">{{ imageState.imageElements.length }}</span>
                <span class="element-count-label">Elements</span>
            </div>
            <VButton text label="Submit leaders" icon="pi pi-check"
                    @click="handleSubmitLeadersClick" :disabled="imageState.selectedLeaderIds.length === 0" />
        </div>
    </div>
</template>
