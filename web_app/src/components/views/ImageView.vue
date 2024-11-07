<script setup lang="ts">
import ImageDisplay from "../ImageDisplay.vue";
import ImageViewNavBar from "../navbars/ImageViewNavBar.vue";
import { ImageAction, useViewStateStore, ViewStates } from "../../stores/viewState";
import InstructionsViewWidget from "../InstructionsWidget.vue";

const viewState = useViewStateStore();
</script>


<template>
    <div id="image-view" class="view">
        <ImageViewNavBar />
        <div v-if="viewState.currentAction === ImageAction.CreateDataset
                && viewState.currentState === ViewStates.ImageViewResult" id="additional-info-bar">
            <p>Select one representant of each category</p>
            <InstructionsViewWidget />
        </div>
        <InstructionsViewWidget v-else />
        <ImageDisplay />
        <component :is="viewState.currentImageViewToolBar"></component>
    </div>
</template>


<style scoped>
#additional-info-bar {
    display: flex;
    width: 100%;
    position: absolute;
    top: 55px;
    background-color: var(--surface-section);
}

#additional-info-bar p {
    padding: 12px 16px;
    width: 80%;
    color: var(--primary-color);
}
</style>

<style>
#additional-info-bar #instructions-button {
    position: relative;
    top: unset;
    right: unset;
    margin: auto;
    margin-right: 7px;
}
</style>
