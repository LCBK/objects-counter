<script setup lang="ts">
import "./ImageViewToolBar.css";
import VButton from "primevue/button";
import { ImageAction, useViewStateStore, ViewStates } from "@/stores/viewState";
import { useImageStateStore } from "@/stores/imageState";
import { parseElementsToImage } from "@/utils";
import { computed, onMounted, ref } from "vue";
import { acceptBackground } from "@/requests/images";


const viewState = useViewStateStore();
const imageState = useImageStateStore();

const pointTypePanel = ref<HTMLElement>();
const positivePointButton = ref<HTMLElement>();
const negativePointButton = ref<HTMLElement>();
const displayPointTypes = ref<Boolean>();

const allButtonsDisabled = computed(() => viewState.isWaitingForResponse);
const confirmButtonDisabled = computed(() => imageState.currentImage.points.length === 0);


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

    await acceptBackground(imageState.currentImage.id).then(response => {
        if (viewState.currentState !== ViewStates.ImageEditPoints) return;

        parseElementsToImage(imageState.currentImage.id, response.elements);

        switch (viewState.currentAction) {
            case ImageAction.AutomaticCounting:
                viewState.setState(ViewStates.ImageViewConfirmCounting);
                break;
            case ImageAction.LeaderCounting:
                viewState.setState(ViewStates.ImageViewSelectLeaders);
                break;
            case ImageAction.CreateDataset:
                viewState.setState(ViewStates.ImageViewSelectLeaders);
                break;
            case ImageAction.CompareWithDataset:
                viewState.setState(ViewStates.ImageViewCompareWithDataset);
                break;
        }
    }).finally(() => {
        viewState.isWaitingForResponse = false;
    });
}


onMounted(() => {
    setPositivePointType();
});
</script>


<template>
    <div class="image-view-tool-bar bar">
        <div class="bar-content tool-bar-content">
            <VButton text label="Add points" icon="pi pi-plus"
                    :disabled="allButtonsDisabled" @click="handleAddClick"
                    :class="viewState.isAddingPoint ? 'active ' : '' + 'add-points'" />
            <VButton text label="Remove points" icon="pi pi-minus"
                    :disabled="allButtonsDisabled" @click="handleRemoveClick"
                    :class="viewState.isRemovingPoint ? 'active ' : '' + 'remove-points'" />
            <VButton text label="Confirm selection" class="confirm-points" icon="pi pi-check"
                    :disabled="confirmButtonDisabled || allButtonsDisabled" @click="handleConfirmBackground" />
        </div>
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

@media screen and (min-width: 340px) {
    #point-types {
        bottom: 110px;
    }
}

@media screen and (min-width: 768px) {
    #point-types {
        /* Half of a toolbar button's length (768px * 1/6) minus half of own width (45px) plus half of bar margin */
        left: calc((768px * 0.1667) - 45px + (50vw - 768px / 2));
    }
}

@media screen and (min-width: 1200px) {
    #point-types {
        /* Half of a toolbar button's length (1200px * 1/6) minus half of own width (45px) plus half of bar margin */
        left: calc((1200px * 0.1667) - 45px + (50vw - 1200px / 2));
    }
}
</style>
