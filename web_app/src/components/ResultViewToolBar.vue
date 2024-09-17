<script setup lang="ts">
import VButton from "primevue/button";
import VSidebar from "primevue/sidebar";
import QuantitiesEntry from "./QuantitiesEntry.vue";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore } from "@/stores/viewState";
import { computed } from "vue";

const imageState = useImageStateStore();
const viewState = useViewStateStore();

const visible = defineModel<boolean>();
const classifications = computed(() => imageState.objectClassifications);
</script>


<template>
    <div class="image-view-tool-bar bar">
        <VButton text label="Details" class="quant" icon="pi pi-list" @click="visible = true" />
        <div class="element-count">
            <span class="element-count-value">{{ imageState.imageElements.length }}</span>
            <span class="element-count-label">Elements</span>
        </div>
        <VButton text label="Adjust" class="edit-selection" icon="pi pi-pencil"
                @click="viewState.setState('editPoints'); imageState.clearResult();" />
    </div>
    <VSidebar v-model:visible="visible" position="bottom" style="height: auto" class="quantities" header="Counted elements">
        <div class="quantities-header">
            <div class="quantities-col">Count</div>
            <div class="quantities-col">Type</div>
            <div class="quantities-col">Show boxes</div>
        </div>
        <QuantitiesEntry v-for="(quantity, index) in classifications" :key="index" :index="quantity.index" />
    </VSidebar>
</template>


<style scoped>
.quantities-header {
    display: flex;
    font-size: 0.75rem;
    font-weight: 300;
    letter-spacing: 0.3px;
    margin: 12px 0 6px 0;
    color: #60a5fa;
}

.quantities-col:nth-child(1) {
    flex-basis: 15%;
    text-align: center;
}

.quantities-col:nth-child(2) {
    flex-basis: 60%;
    text-indent: 10px;
}

.quantities-col:nth-child(3) {
    flex-basis: 25%;
    text-align: center;
}

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

.element-count {
    display: flex;
    flex-direction: column;
    color: #60a5fa;
    text-align: center;
    justify-content: space-between;
    margin-top: -20px;
    background-color: #1c1c20;
    border-top-left-radius: 30px;
    border-top-right-radius: 30px;
    padding: 10px 25px;
    -webkit-box-shadow: 0px 0px 6px 0px rgba(9, 9, 11, 0.5);
    -moz-box-shadow: 0px 0px 6px 0px rgba(9, 9, 11, 0.5);
    box-shadow: 0px 0px 6px 0px rgba(9, 9, 11, 0.5);
}

.element-count-value {
    display: block;
    font-weight: bold;
    font-size: 2.25rem;
}

.element-count-label {
    display: block;
}
</style>
