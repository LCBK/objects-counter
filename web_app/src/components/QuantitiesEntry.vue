<script setup lang="ts">
const props = defineProps({
    classification: {
        type: String,
        required: true
    },
    count: {
        type: Number,
        required: true
    },
    isNameAssigned: {
        type: Boolean,
        required: true
    }
});

// todo: enable user to name classifications
</script>


<template>
    <div class="quantity">
        <div class="quantity-count">{{ props.count }}</div>
        <div class="quantity-classification">{{ isNameAssigned ? props.classification : "Type " + props.classification }}</div>
    </div>
</template>


<style scoped>
.quantity {
    display: flex;
    flex-direction: row;
    margin: 15px 0;
    align-items: center;
}

.quantity:not(:first-child) {
    border-top: 1px solid #282828;
}

.quantity-classification {
    margin-left: 20px;
    font-size: 1rem;
    font-weight: 300;
    letter-spacing: 0.3px;
}

.quantity-count {
    font-size: 1.6rem;
    text-align: center;
    width: 30px;
    font-weight: 500;
}
</style>
