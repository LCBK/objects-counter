<script setup lang="ts">
import LoadingSpinner from "../LoadingSpinner.vue";
</script>


<template>
    <div id="loading-view" class="view">
        <LoadingSpinner />
        <p class="uploading-text">Uploading...</p>
    </div>
</template>


<style scoped>
#loading-view {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

#loading-view .loader {
    width: 64px;
    height: 64px;
    margin-bottom: 20px;
}

#loading-view .uploading-text {
    color: var(--primary-color);
    font-weight: 700;
    letter-spacing: 0.5px;
    font-size: 1.1rem;
}
</style>
