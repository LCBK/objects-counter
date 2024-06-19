<script setup lang="ts">
import VCheckbox from "primevue/checkbox";

const props = defineProps({
    index: {
        type: Number,
        required: true
    },
    class: {
        type: String,
        required: true
    },
    count: {
        type: Number,
        required: true
    }
});
</script>


<template>
    <div class="quantity">
        <VCheckbox :binary="true" class="quantity-checkbox" />
        <div class="quantity-class">{{ props.class }}</div>
        <div class="quantity-count">{{ props.count }}</div>
    </div>
</template>


<style scoped>
.quantity {
    display: flex;
    flex-direction: row;
}

.quantity-checkbox {
    margin-right: 10px;
}

.quantity-class {
    flex-grow: 2;
}

.quantity-count {
    flex-grow: 1;
}
</style>
