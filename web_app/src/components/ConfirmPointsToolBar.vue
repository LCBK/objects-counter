<script setup lang="ts">
import VButton from "primevue/button";
import { useViewStateStore } from "@/stores/viewState";
import { useImageStateStore } from "@/stores/imageState";
import { boundingBoxColors, config, endpoints } from "@/config";
import { sendRequest } from "@/utils";
import { computed } from "vue";

const viewState = useViewStateStore();
const imageState = useImageStateStore();

const allButtonsDisabled = computed(() => viewState.isWaitingForResponse);

// Iterates over image elements and assignes appropriate classifications to imageState.objectClassifications
function assignObjectClassifications() {
    const countedClassifications: Array<string> = [];
    const classificationQuantities: Array<number> = [];

    // Count occurences of classifications
    imageState.imageElements.forEach(element => {
        if (!countedClassifications.includes(element.classification)) {
            countedClassifications.push(element.classification);
            classificationQuantities.push(1);
        }
        else {
            const index = countedClassifications.indexOf(element.classification);
            classificationQuantities[index]++;
        }
    });

    // Sort classifications by element count
    const sortedClassifications: Array<[string, number]> = [];
    countedClassifications.forEach((element, index) => {
        sortedClassifications.push([element, classificationQuantities[index]]);
    });
    sortedClassifications.sort((a, b) => a[0] > b[0] ? 1 : -1);

    // Assign classifications and their indices to elements
    imageState.objectClassifications = [];
    sortedClassifications.forEach((classification, index) => {
        imageState.objectClassifications.push({ 
            index: index,
            classificationName: classification[0],
            count: classification[1],
            isNameAssigned: false,
            showBoxes: true,
            boxColor: boundingBoxColors[index % boundingBoxColors.length]
        });
        imageState.imageElements.forEach(element => {
            if (element.classification == classification[0]) {
                element.classificationIndex = index;
            }
        });
        index++;
    });
}

function handleConfirmBackground() {
    const requestUri = config.serverUri + endpoints.acceptBackground.replace("{image_id}", imageState.imageId.toString());
    const requestData = JSON.stringify({});
    const responsePromise = sendRequest(requestUri, requestData, "POST");

    viewState.isWaitingForResponse = true;
    
    // Backend returns counted and classified image elements
    responsePromise.then((response) => {
        viewState.isWaitingForResponse = false;

        // Change snake_case to camelCase for keys
        const parsedResponse = JSON.parse(response
                .replaceAll("top_left", "topLeft")
                .replaceAll("bottom_right", "bottomRight"));
        imageState.imageElements = parsedResponse.objects;

        assignObjectClassifications();

        viewState.setState('viewResult');
    });
}
</script>


<template>
    <div class="image-view-tool-bar bar">
        <VButton text label="Edit selection" class="edit-selection" icon="pi pi-pencil"
                :disabled="allButtonsDisabled" @click="viewState.setState('editPoints')" />
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
