<script setup lang="ts">
import ImageDisplay from "../ImageDisplay.vue";
import ImageViewNavBar from "../navbars/ImageViewNavBar.vue";
import { useViewStateStore } from "../../stores/viewState";
import InstructionsViewWidget from "../InstructionsWidget.vue";

const viewState = useViewStateStore();
</script>


<template>
    <div id="image-view" class="view">
        <ImageViewNavBar />
        <InstructionsViewWidget />
        <ImageDisplay />
        <component :is="viewState.currentImageViewToolBar"></component>
    </div>
</template>


<style scoped>

</style>
