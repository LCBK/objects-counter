<script setup lang="ts">
import MainView from "./components/MainView.vue";
import ImageView from "./components/ImageView.vue";
import LoadingView from "./components/LoadingView.vue";
import { useImageStateStore } from "./stores/imageState";

const imageState = useImageStateStore();
</script>

<template>
    <header>

    </header>
    <main>
        <Transition name="slide">
            <MainView v-if="!imageState.isUploaded && !imageState.isUploading" />
            <LoadingView v-else-if="!imageState.isUploaded && imageState.isUploading" />
            <ImageView v-else-if="imageState.isUploaded" />
        </Transition>
    </main>
</template>

<style scoped>
main {
    width: 100vw;
}

.slide-enter-active,
.slide-leave-active {
    transition: 0.6s ease;
    transition-property: transform, background-color;
    position: fixed;
    top: 0;
    left: 0;
}

.slide-enter-active::after,
.slide-leave-active::after {
    width: 100vw;
    height: 100vh;
    height: 100dvh;
    display: block;
    position: absolute;
    content: "";
    top: 0;
    left: 0;
    z-index: 100;
    background-color: var(--color-background);
    opacity: 0.0;
}

.slide-leave-to::after {
    animation: page-fade 0.6s;
}

.slide-enter-from {
    transform: translateX(100%);
}

.slide-enter-to,
.slide-leave-from {
    transform: translateX(0%);
}

.slide-leave-to {
    transform: translateX(-100%);
}

@keyframes page-fade {
    0% {
        opacity: 0.0;
    }

    100% {
        opacity: 1.0;
    }
}
</style>
