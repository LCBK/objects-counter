<script setup lang="ts">
import LoadingSpinner from "./LoadingSpinner.vue";
</script>


<template>
    <div id="loading-view" class="view">
        <LoadingSpinner />
    </div>
</template>


<style scoped>
#loading-view .loader {
    width: 64px;
    height: 64px;
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
}
</style>
