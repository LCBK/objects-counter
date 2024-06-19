<script setup lang="ts">
import VButton from "primevue/button";
import { useImageStateStore } from "@/stores/imageState";

function onBack() : void {
    useImageStateStore().reset();
}
</script>


<template>
    <div class="image-view-bar">
        <VButton label="Back" outlined icon="pi pi-chevron-left" @click="onBack()" />
    </div>
</template>


<style scoped>
.image-view-bar {
    padding: 8px;
}
</style>
