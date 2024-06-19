<script setup lang="ts">
import VButton from "primevue/button";
import { useImageStateStore } from "@/stores/imageState";

function onBack() : void {
    useImageStateStore().reset();
}
</script>


<template>
    <div class="image-view-nav-bar">
        <VButton label="Back" outlined icon="pi pi-chevron-left" @click="onBack()" />
    </div>
</template>


<style scoped>
.image-view-nav-bar {
    padding: 8px;
}
</style>
