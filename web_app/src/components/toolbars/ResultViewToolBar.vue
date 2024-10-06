<script setup lang="ts">
import VButton from "primevue/button";
import VSidebar from "primevue/sidebar";
import QuantitiesEntry from "../QuantitiesEntry.vue";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
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
                @click="viewState.setState(ViewStates.ImageEditPoints); imageState.clearResult();" />
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
    color: var(--primary-color);
    user-select: none;
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
    color: var(--primary-color);
    text-align: center;
    justify-content: space-between;
    margin-top: -20px;
    background-color: var(--surface-card);
    border-top-left-radius: 30px;
    border-top-right-radius: 30px;
    padding: 10px 25px;
    -webkit-box-shadow: 0px 0px 6px 0px var(--color-shadow);
    -moz-box-shadow: 0px 0px 6px 0px var(--color-shadow);
    box-shadow: 0px 0px 6px 0px var(--color-shadow);
}

.element-count-value {
    display: block;
    font-weight: 700;
    font-size: 2.25rem;
}

.element-count-label {
    display: block;
    font-weight: 500;
}
</style>

<style>
.quantities .p-sidebar-header-content {
    color: var(--primary-color);
    font-weight: 400;
    letter-spacing: 0.3px;
    user-select: none;
}

.quantity-switch .p-inputswitch-input {
    width: 40px;
    left: 50%;
    transform: translateX(-50%);
}

.quantity-switch .p-inputswitch-slider {
    width: 40px;
    margin: 0 auto;
}
</style>
