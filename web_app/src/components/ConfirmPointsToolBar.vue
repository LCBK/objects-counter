<script setup lang="ts">
import VButton from "primevue/button";
import { useViewStateStore } from "@/stores/viewState";

const viewState = useViewStateStore();
</script>


<template>
    <div class="image-view-tool-bar bar">
        <VButton text label="Edit selection" class="edit-selection" icon="pi pi-pencil" />
        <VButton text label="Confirm selection" class="confirm-selection" icon="pi pi-check"
                @click="viewState.setState('viewResult')" />
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
</style>
