<script setup lang="ts">
import VButton from "primevue/button";
import VSidebar from "primevue/sidebar";
import QuantitiesEntry from "./QuantitiesEntry.vue";
import { useImageStateStore } from "@/stores/imageState";
import type { Quantity } from '@/types';
import { computed } from "vue";

const visible = defineModel<boolean>();
const imageState = useImageStateStore();

const quantities: Array<Quantity> = [];
const countedClasses: Array<string> = [];
const classQuantities: Array<number> = [];

imageState.results.forEach((result) => {
    if (!countedClasses.includes(result.class)) {
        countedClasses.push(result.class);
        classQuantities.push(1);
    }
    else {
        const classIndex = countedClasses.indexOf(result.class);
        classQuantities[classIndex]++;
    }
});

let quantitiesIndex = 0;
countedClasses.forEach((c) => {
    quantities.push({ index: quantitiesIndex, class: c, count: classQuantities[quantitiesIndex++] });
});

const orderedQuantities = computed(() => {
    const arr = Array.from(quantities).sort((a, b) => {
        return a.count < b.count ? 1 : 0;
    });
    return arr;
});

const elementCount = imageState.results.length;
</script>


<template>
    <div class="image-view-tool-bar bar">
        <VButton text v-bind:label="elementCount + ' elements'" class="quant" icon="pi pi-list" @click="visible = true" />
    </div>
    <VSidebar v-model:visible="visible" position="bottom" style="height: auto">
        <QuantitiesEntry v-for="(quantity, index) in orderedQuantities" :key="index"
                v-bind:index="index" v-bind:class="quantity.class"
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

.image-view-tool-bar .quant .p-button-label {
    font-size: 1.2rem;
}
</style>
