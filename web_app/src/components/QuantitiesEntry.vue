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
    },
    showBoxes: {
        type: Boolean,
        required: true
    }
});

// todo: enable user to name classifications
// todo: implement changing showBoxes
</script>


<template>
    <div class="quantity">
        <div class="quantity-count">{{ props.count }}</div>
        <div class="quantity-classification">{{ isNameAssigned ? props.classification : "Type " + props.classification }}</div>
        <input type="checkbox" class="quantity-checkbox" :checked="props.showBoxes">
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
    border-top: 1px solid #282828;
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

.quantity-checkbox {
    flex-basis: 25%;
}
</style>
