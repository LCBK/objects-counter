<script setup lang="ts">
import ImageDisplay from "./ImageDisplay.vue";
import ImageViewNavBar from "./ImageViewNavBar.vue";
import ImageViewToolBar from "./ImageViewToolBar.vue";
</script>


<template>
    <div id="image-view" class="view">
        <ImageViewNavBar />
        <ImageDisplay />
        <ImageViewToolBar />
    </div>
</template>


<style scoped>

</style>
