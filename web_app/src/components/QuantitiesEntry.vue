<script setup lang="ts">
import { useImageStateStore } from "@/stores/imageState";
import VInputSwitch from "primevue/inputswitch";
import { computed } from "vue";

// This component will change imageState, it will update its parents.
// That's why we have only an index prop, which we use to access and update object classification properties.

const props = defineProps({
    index: {
        type: Number,
        required: true
    }
});

const imageState = useImageStateStore();

// These are not props, because they control parents' states by updating imageState.
const count = computed(() => imageState.objectClassifications[props.index].count);
const classificationName = computed(() => imageState.objectClassifications[props.index].classificationName);
const isNameAssigned = computed(() => imageState.objectClassifications[props.index].isNameAssigned);
const showBoxes = computed({
    get() {
        return imageState.objectClassifications[props.index].showBoxes;
    },
    set(value) {
        imageState.objectClassifications[props.index].showBoxes = value;
    }
});

// todo: enable user to name classifications
</script>


<template>
    <div class="quantity">
        <div class="quantity-count">{{ count }}</div>
        <div class="quantity-classification">
            {{ isNameAssigned ? classificationName : "Type " + classificationName }}
        </div>
        <VInputSwitch class="quantity-switch" v-model="showBoxes" />
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

.quantity-classification {
    flex-basis: 60%;
    font-size: 1rem;
    font-weight: 300;
    letter-spacing: 0.3px;
    text-indent: 10px;
}

.quantity-switch {
    flex-basis: 25%;
}
</style>
