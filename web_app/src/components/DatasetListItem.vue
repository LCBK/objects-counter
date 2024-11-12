<script setup lang="ts">
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
    },
    thumbnailUri: {
        type: String,
        required: false
    }
});
</script>


<template>
    <div class="dataset-item">
        <img :src="props.thumbnailUri" alt="No thumbnail" class="dataset-item-image" />
        <div>
            <div class="dataset-item-name">{{ name }}</div>
            <div class="dataset-item-date">{{ new Date(timestamp).toISOString().split("T")[0] }}</div>
            <div class="dataset-item-time">{{ new Date(timestamp).toLocaleTimeString() }}</div>
        </div>
    </div>
</template>


<style scoped>
.dataset-item {
    display: flex;
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

.dataset-item-image {
    height: 100%;
    border-radius: 8px;
    margin-right: 16px;
    max-width: 72px;
    max-height: 72px;
    aspect-ratio: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
}
</style>
