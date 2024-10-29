<script setup lang="ts">
import VButton from "primevue/button";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { config, endpoints } from "@/config";
import { useImageStateStore } from "@/stores/imageState";
import { parseClassificationsFromResponse, sendRequest } from "@/utils";
import { computed, onMounted, ref } from "vue";


const viewState = useViewStateStore();
const imageState = useImageStateStore();

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

function handleConfirmBackground() {
    const requestUri = config.serverUri + endpoints.acceptBackground.replace("{image_id}", imageState.imageId.toString());
    const requestData = JSON.stringify({});
    const responsePromise = sendRequest(requestUri, requestData, "POST");

    viewState.isWaitingForResponse = true;

    // Backend returns counted and classified image elements
    responsePromise.then((response) => {
        viewState.isWaitingForResponse = false;
        parseClassificationsFromResponse(JSON.parse(response.data).classifications);
        if (JSON.parse(response.data).id) imageState.resultId = JSON.parse(response.data).id;
        if (viewState.currentState !== ViewStates.ImageEditPoints) return;
        viewState.setState(ViewStates.ImageViewResult);
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
