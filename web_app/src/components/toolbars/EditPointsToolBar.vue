<script setup lang="ts">
import "./ImageViewToolBar.css";
import VButton from "primevue/button";
import { ImageAction, useViewStateStore, ViewStates } from "@/stores/viewState";
import { config, endpoints } from "@/config";
import { useImageStateStore } from "@/stores/imageState";
import { parseClassificationsFromResponse, parseElementsFromResponse, sendRequest } from "@/utils";
import { computed, onMounted, ref } from "vue";
import { useUserStateStore } from "@/stores/userState";


const viewState = useViewStateStore();
const imageState = useImageStateStore();
const userState = useUserStateStore();

const pointTypePanel = ref<HTMLElement>();
const positivePointButton = ref<HTMLElement>();
const negativePointButton = ref<HTMLElement>();
const displayPointTypes = ref<Boolean>();

const allButtonsDisabled = computed(() => viewState.isWaitingForResponse);
const confirmButtonDisabled = computed(() => imageState.points.length === 0);


function setPositivePointType() {
    viewState.isPointTypePositive = true;
    positivePointButton.value!.classList.add("checked");
    negativePointButton.value!.classList.remove("checked");
}

function setNegativePointType() {
    viewState.isPointTypePositive = false;
    positivePointButton.value!.classList.remove("checked");
    negativePointButton.value!.classList.add("checked");
}

function handleAddClick() {
    viewState.toggleAddPoint();
    displayPointTypes.value = !displayPointTypes.value;
}

function handleRemoveClick() {
    viewState.toggleRemovePoint();
    displayPointTypes.value = false;
}

async function handleConfirmBackground() {
    viewState.isWaitingForResponse = true;

    if (viewState.isEditingExistingResult && viewState.currentAction !== ImageAction.CreateDataset) {
        if (userState.isLoggedIn) {
            const deleteRequestUri = config.serverUri + endpoints.deleteResult.replace("{result_id}", imageState.resultId.toString());
            const deleteRequestData = JSON.stringify({});
            await sendRequest(deleteRequestUri, deleteRequestData, "DELETE");
        }

        viewState.isEditingExistingResult = false;
    }

    const requestUri = config.serverUri + endpoints.acceptBackground.replace("{image_id}", imageState.imageId.toString());
    const requestData = JSON.stringify({
        as_dataset: viewState.currentAction === ImageAction.CreateDataset
    });
    const responsePromise = sendRequest(requestUri, requestData, "POST");

    responsePromise.then((response) => {
        viewState.isWaitingForResponse = false;
        if (viewState.currentState !== ViewStates.ImageEditPoints) return;

        if (viewState.currentAction === ImageAction.CreateDataset) {
            // Backend responds with elements without classifications, only for leader selection
            parseElementsFromResponse(response.data.elements);
            if (response.data.id) imageState.resultId = response.data.id;
        }
        else {
            // Otherwise the response contains classifications
            parseClassificationsFromResponse(JSON.parse(response.data).classifications);
            if (JSON.parse(response.data).id) imageState.resultId = JSON.parse(response.data).id;
        }

        switch (viewState.currentAction) {
            case ImageAction.SimpleCounting:
                viewState.setState(ViewStates.ImageViewCountingResult);
                break;
            case ImageAction.CreateDataset:
                viewState.setState(ViewStates.ImageViewCreateDataset);
                break;
            case ImageAction.CompareWithDataset:
                viewState.setState(ViewStates.ImageViewCompareWithDataset);
                break;
        }
    });
}


onMounted(() => {
    setPositivePointType();
});
</script>


<template>
    <div class="image-view-tool-bar bar">
        <VButton text label="Add points" icon="pi pi-plus"
                :disabled="allButtonsDisabled" @click="handleAddClick"
                :class="viewState.isAddingPoint ? 'active ' : '' + 'add-points'" />
        <VButton text label="Remove points" icon="pi pi-minus"
                :disabled="allButtonsDisabled" @click="handleRemoveClick"
                :class="viewState.isRemovingPoint ? 'active ' : '' + 'remove-points'" />
        <VButton text label="Confirm selection" class="confirm-points" icon="pi pi-check"
                :disabled="confirmButtonDisabled || allButtonsDisabled" @click="handleConfirmBackground" />
    </div>
    <div id="point-types" ref="pointTypePanel" v-show="displayPointTypes">
        <div id="positive-point" ref="positivePointButton" @click="setPositivePointType">+</div>
        <div id="negative-point" ref="negativePointButton" @click="setNegativePointType">-</div>
    </div>
</template>


<style scoped>
#point-types {
    z-index: 200;
    position: absolute;
    bottom: 100px;
    left: calc(16.67vw - 45px);     /* Half of a toolbar button's length minus half of type selector width */
    display: flex;
    justify-content: space-around;
    color: var(--text-color);
    font-weight: 700;
    font-size: 1.3rem;
    line-height: 2rem;
}

.light #point-types {
    color: white;
}

#point-types > div:not(.checked) {
    color: var(--text-color-secondary);
}

.light #point-types > div:not(.checked) {
    color: white;
}

#point-types > div {
    width: 45px;
    height: 35px;
    z-index: 200;
    text-align: center;
    transition: 0.2s;
}

#positive-point {
    background-color: rgba(96, 165, 250, 0.4);
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
}

#negative-point {
    background-color: rgba(255, 98, 89, 0.4);
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
}

#positive-point.checked {
    background-color: rgba(96, 165, 250, 1);
}

#negative-point.checked {
    background-color: rgba(255, 98, 89, 1);
}
</style>
