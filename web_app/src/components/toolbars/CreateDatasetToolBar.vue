<script setup lang="ts">
import "./ImageViewToolBar.css";
import VButton from "primevue/button";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { config, endpoints } from "@/config";
import { parseClassificationsFromResponse, sendRequest } from "@/utils";


const imageState = useImageStateStore();
const viewState = useViewStateStore();


function handleReturnClick() {
    viewState.setState(ViewStates.ImageEditPoints);
    viewState.showBackground = true;
    viewState.isEditingExistingResult = true;
    imageState.clearResult();
}

function handleSubmitLeadersClick() {
    submitClassificationLeaders();
}

function submitClassificationLeaders() {
    const requestUri = config.serverUri + endpoints.classifyByLeaders.replace("{image_id}", imageState.imageId.toString());
    const requestData = JSON.stringify({
        leaders: imageState.selectedLeaderIds
    });
    const requestPromise = sendRequest(requestUri, requestData, "POST");

    viewState.isWaitingForResponse = true;
    requestPromise.then((response) => {
        if (response.status === 200) {
            imageState.clearResult();
            parseClassificationsFromResponse(response.data.classifications);
            viewState.setState(ViewStates.ImageViewConfirmDataset);
        }
        else {
            console.error("Failed to submit dataset leaders");
        }
        viewState.isWaitingForResponse = false;
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
