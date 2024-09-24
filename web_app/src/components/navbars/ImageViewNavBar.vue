<script setup lang="ts">
import VButton from "primevue/button";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore } from "@/stores/viewState";

const viewState = useViewStateStore();

function onBack() : void {
    useImageStateStore().reset();
    useViewStateStore().reset();
}
</script>


<template>
    <div class="image-view-nav-bar bar">
        <VButton text rounded icon="pi pi-chevron-left" @click="onBack()" />
        <h2 id="image-view-title">{{ viewState.currentNavBarTitle }}</h2>
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

.image-view-nav-bar h2 {
    color: var(--primary-color);
    font-size: 1.3rem;
    line-height: 38px;
    letter-spacing: 0.4px;
    font-weight: 600;
}
</style>
