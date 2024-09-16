<script setup lang="ts">
const props = defineProps({
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
        <div class="quantity-count">{{ props.count }}</div>
        <div class="quantity-class">{{ props.class }}</div>
    </div>
</template>


<style scoped>
.quantity {
    display: flex;
    flex-direction: row;
    margin: 15px 0;
    align-items: center;
    border-bottom: 1px solid #282828;
}

.quantity-class {
    margin-left: 10px;
    font-size: 1rem;
}

.quantity-count {
    font-size: 1.6rem;
    text-align: center;
    width: 30px;
}
</style>
