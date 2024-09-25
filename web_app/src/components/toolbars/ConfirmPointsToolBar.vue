<script setup lang="ts">
import VButton from "primevue/button";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { useImageStateStore } from "@/stores/imageState";
import { boundingBoxColors, config, endpoints } from "@/config";
import { sendRequest } from "@/utils";
import { computed } from "vue";

const viewState = useViewStateStore();
const imageState = useImageStateStore();

const allButtonsDisabled = computed(() => viewState.isWaitingForResponse);

function handleConfirmBackground() {
    const requestUri = config.serverUri + endpoints.acceptBackground.replace("{image_id}", imageState.imageId.toString());
    const requestData = JSON.stringify({});
    const responsePromise = sendRequest(requestUri, requestData, "POST");

    viewState.isWaitingForResponse = true;
    
    // Backend returns counted and classified image elements
    responsePromise.then((response) => {
        viewState.isWaitingForResponse = false;

        JSON.parse(response.data).classifications.forEach((element: any, index: number) => {
            imageState.objectClassifications.push({
                index: index,
                classificationName: element.classification,
                count: element.objects.length,
                isNameAssigned: false,
                showBoxes: true,
                boxColor: boundingBoxColors[index % boundingBoxColors.length]
            });
            element.objects.forEach((object: any) => {
                imageState.imageElements.push({
                    topLeft: object.top_left,
                    bottomRight: object.bottom_right,
                    certainty: object.certainty,
                    classificationIndex: index
                });
            });
        });

        viewState.setState(ViewStates.ImageViewResult);
    });
}
</script>


<template>
    <div class="image-view-tool-bar bar">
        <VButton text label="Edit selection" class="edit-selection" icon="pi pi-pencil"
                :disabled="allButtonsDisabled" @click="viewState.setState(ViewStates.ImageEditPoints)" />
        <VButton text label="Confirm selection" class="confirm-selection" icon="pi pi-check"
                :disabled="allButtonsDisabled" @click="handleConfirmBackground" />
    </div>
</template>


<style scoped>
.image-view-tool-bar {
    padding: 0;
    position: fixed;
    bottom: 0;
    height: 90px;
    align-items: stretch;
}

.image-view-tool-bar > button {
    flex-direction: column;
    padding: 12px 1rem;
    justify-content: space-between;
    flex: 1 1 0px;
}
</style>
