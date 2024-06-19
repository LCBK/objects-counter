<script setup lang="ts">
import { onMounted } from 'vue';
import VButton from "primevue/button";
import VSidebar from "primevue/sidebar";
import QuantitiesEntry from "./QuantitiesEntry.vue";
import { useImageStateStore } from "@/stores/imageState";
import type { Quantity } from '@/types';

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
</script>


<template>
    <div class="image-view-tool-bar">
        <VButton label="Show quantities" outlined icon="pi pi-list" @click="visible = true" />
    </div>
    <VSidebar v-model:visible="visible" position="bottom" style="height: auto">
        <QuantitiesEntry v-for="(quantity, index) in quantities" :key="index"
                v-bind:index="index" v-bind:class="quantity.class" 
                v-bind:count="quantity.count" />
    </VSidebar>
</template>


<style scoped>
.image-view-tool-bar {
    padding: 8px;
}
</style>
