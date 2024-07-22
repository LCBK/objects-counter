<script setup lang="ts">
import VButton from "primevue/button";
import { useViewStateStore } from "@/stores/viewState";

const viewState = useViewStateStore();
</script>


<template>
    <div class="image-view-tool-bar bar">
        <VButton text label="Add point" class="add-point" icon="pi pi-plus" />
        <VButton text label="Edit points" class="edit-points" icon="pi pi-list" />
        <VButton text label="Confirm points" class="confirm-points" icon="pi pi-check"
                @click="viewState.setState('confirmBackground')" />
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
