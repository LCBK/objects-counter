<script setup lang="ts">
import "./ImageViewToolBar.css";
import VButton from "primevue/button";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { config, endpoints } from "@/config";
import { parseClassificationsFromDatasetResponse, sendRequest } from "@/utils";


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

function submitClassificationLeaders() {
    const requestUri = config.serverUri + endpoints.markLeaders.replace("{image_id}", imageState.imageId.toString());
    const requestData = JSON.stringify({
        leaders: imageState.selectedLeaderIds
    });
    const requestPromise = sendRequest(requestUri, requestData, "POST");

    viewState.isWaitingForResponse = true;
    requestPromise.then((leadersResponse) => {
        if (leadersResponse.status === 200) {
            const createDatasetUri = config.serverUri + endpoints.createDataset;
            const createDatasetRequestData = JSON.stringify({
                name: "temporary no. " + imageState.imageId
            });

            const createDatasetRequestPromise = sendRequest(createDatasetUri, createDatasetRequestData, "POST");
            createDatasetRequestPromise.then((createDatasetResponse) => {
                if (createDatasetResponse.status === 201) {
                    imageState.datasetId = createDatasetResponse.data;

                    const addDatasetImageUri = config.serverUri + endpoints.addImageToDataset.replace("{dataset_id}", imageState.datasetId.toString());
                    const addDatasetImageRequestData = JSON.stringify({
                        image_id: imageState.imageId,
                        classifications: imageState.selectedLeaderIds.map((id: any, index: number) => {
                            return {
                                name: index,
                                leader_id: id
                            }
                        })
                    });

                    const addDatasetImageRequestPromise = sendRequest(addDatasetImageUri, addDatasetImageRequestData, "POST");
                    addDatasetImageRequestPromise.then((addDatasetImageResponse) => {
                        if (addDatasetImageResponse.status === 200) {
                            imageState.clearResult();
                            parseClassificationsFromDatasetResponse(addDatasetImageResponse.data.images[0].elements);
                            viewState.setState(ViewStates.ImageViewConfirmDataset);
                        }
                        else {
                            console.error("Failed to add image to dataset for image " + imageState.imageId);
                        }
                        viewState.isWaitingForResponse = false;
                    });
                }
                else {
                    console.error("Failed to create dataset for image " + imageState.imageId);
                }
            });
        }
        else {
            console.error("Failed to submit dataset leaders for image " + imageState.imageId);
        }
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
