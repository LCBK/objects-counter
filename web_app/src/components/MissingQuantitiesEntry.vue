<script setup lang="ts">
import { useImageStateStore } from "@/stores/imageState";
import { formatClassificationName } from "@/utils";
import VInputSwitch from "primevue/inputswitch";
import { computed } from "vue";

const props = defineProps({
    name: {
        type: String,
        required: true
    }
});

const imageState = useImageStateStore();

const difference = computed(() => {
    return imageState.comparisonDifference[props.name];
});
</script>


<template>
    <div class="quantity">
        <div class="diff quantity-count">
            0 <span class="diff-value diff-negative">({{ difference }})</span>
        </div>
        <div class="quantity-classification">
            {{ formatClassificationName(name) }}
        </div>
        <VInputSwitch class="quantity-switch" disabled />
    </div>
</template>


<style scoped>
.quantity {
    display: flex;
    padding-bottom: 3px;
    align-items: center;
}

.quantity:not(:first-child) {
    padding-top: 3px;
    border-top: 1px solid var(--surface-border);
}

.quantity-count {
    flex-basis: 15%;
    font-size: 1.6rem;
    font-weight: 500;
    text-indent: 0;
    text-align: center;
}

.quantity-count.diff {
    flex-basis: 20%;
}

.quantity-classification {
    flex-basis: 60%;
    font-size: 1rem;
    font-weight: 300;
    letter-spacing: 0.3px;
    text-indent: 10px;
    cursor: pointer;
}

.quantity-switch {
    flex-basis: 25%;
}

.diff-value {
    font-size: 0.9rem;
    font-weight: 400;
}

.diff-negative {
    color: var(--color-error);
}
</style>
