<script setup lang="ts">
import ImageDisplay from "../ImageDisplay.vue";
import ImageViewNavBar from "../ImageViewNavBar.vue";
import { useViewStateStore } from "../../stores/viewState";

const viewState = useViewStateStore();
</script>


<template>
    <div id="image-view" class="view">
        <ImageViewNavBar />
        <ImageDisplay />
        <component :is="viewState.currentImageViewToolBar"></component>
    </div>
</template>


<style scoped>

</style>
