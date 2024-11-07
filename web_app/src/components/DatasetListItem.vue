<script setup lang="ts">
import { defineProps } from "vue";


const props = defineProps({
    id: {
        type: Number,
        required: true
    },
    name: {
        type: String,
        required: true
    },
    timestamp: {
        type: Number,
        required: true
    }
    // TODO: add thumbnail/images
});
</script>


<template>
    <div class="dataset-item">
        <div class="dataset-item-contents">
            <div class="dataset-item-name">{{ name }}</div>
            <div class="dataset-item-date">{{ new Date(timestamp).toISOString().split("T")[0] }}</div>
            <div class="dataset-item-time">{{ new Date(timestamp).toLocaleTimeString() }}</div>
        </div>
    </div>
</template>


<style scoped>
.dataset-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    user-select: none;
    cursor: pointer;
}

.dataset-item-name {
    font-weight: 500;
    font-size: 1rem;
    color: var(--text-color);
}

.dataset-item-date,
.dataset-item-time {
    font-weight: 500;
    font-size: 0.8rem;
    color: var(--text-color-secondary);
}
</style>
