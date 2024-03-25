<script setup lang="ts">
import ImageInput from "./components/ImageInput.vue";
import ImageDisplay from "./components/ImageDisplay.vue";
import { useImageStateStore } from "./stores/imageState";

const imageState = useImageStateStore();
</script>

<template>
    <header>
    
    </header>
    <main>
        <Transition>
            <ImageInput v-if="!imageState.isUploaded" />
            <ImageDisplay v-else />
        </Transition>
    </main>
</template>

<style scoped>
main {
    width: 100vw;
}
</style>
