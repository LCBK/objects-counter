<script setup lang="ts">
import VButton from "primevue/button";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore } from "@/stores/viewState";

function onBack() : void {
    useImageStateStore().reset();
    useViewStateStore().reset();
}
</script>


<template>
    <div class="image-view-nav-bar bar">
        <VButton text rounded icon="pi pi-chevron-left" @click="onBack()" />
        <VButton text rounded icon="pi pi-cog" @click="onBack()" />
    </div>
</template>


<style scoped>
.image-view-nav-bar {
    padding: 8px;
    position: fixed;
    top: 0;
    justify-content: space-between;
}
</style>
