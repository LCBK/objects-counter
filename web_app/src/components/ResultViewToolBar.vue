<script setup lang="ts">
import VButton from "primevue/button";
import VSidebar from "primevue/sidebar";
import QuantitiesEntry from "./QuantitiesEntry.vue";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore } from "@/stores/viewState";
import type { ObjectQuantity } from '@/types';
import { computed } from "vue";

const visible = defineModel<boolean>();
const imageState = useImageStateStore();
const viewState = useViewStateStore();

const quantities: Array<ObjectQuantity> = [];
const countedClasses: Array<string> = [];
const classQuantities: Array<number> = [];

imageState.imageElements.forEach((result) => {
    if (!countedClasses.includes(result.classification)) {
        countedClasses.push(result.classification);
        classQuantities.push(1);
    }
    else {
        const classIndex = countedClasses.indexOf(result.classification);
        classQuantities[classIndex]++;
    }
});

let quantitiesIndex = 0;
countedClasses.forEach((c) => {
    quantities.push({ classification: c, count: classQuantities[quantitiesIndex++] });
});

const orderedQuantities = computed(() => {
    const arr = Array.from(quantities).sort((a, b) => {
        return a.count < b.count ? 1 : 0;
    });
    return arr;
});
</script>


<template>
    <div class="image-view-tool-bar bar">
        <VButton text label="Details" class="quant" icon="pi pi-list"
                @click="visible = true" />
        <div class="element-count">
            <span class="element-count-value">{{ imageState.imageElements.length }}</span>
            <span class="element-count-label">elements</span>
        </div>
        <VButton text label="Adjust" class="edit-selection" icon="pi pi-pencil"
                @click="viewState.setState('editPoints'); imageState.clearResult();" />
    </div>
    <VSidebar v-model:visible="visible" position="bottom" style="height: auto">
        <QuantitiesEntry v-for="(quantity, index) in orderedQuantities" :key="index"
                v-bind:index="index" v-bind:class="quantity.classification"
                v-bind:count="quantity.count" />
    </VSidebar>
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
