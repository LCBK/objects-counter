<script setup lang="ts">
import VButton from 'primevue/button';
import { useImageStateStore } from '@/stores/imageState';
import { computed } from 'vue';


const imageState = useImageStateStore();

const imageBackDisabled = computed(() => imageState.currentImageIndex === 0);
const imageNextDisabled = computed(() => imageState.currentImageIndex === imageState.images.length - 1);


function handleImageBack() {
    if (imageState.currentImageIndex > 0) {
        imageState.currentImageIndex--;
        window.dispatchEvent(new Event("image-changed"));
    }
}

function handleImageNext() {
    if (imageState.currentImageIndex < imageState.images.length - 1) {
        imageState.currentImageIndex++;
        window.dispatchEvent(new Event("image-changed"));
    }
}
</script>

<template>
    <div class="navigation-overlay">
        <div class="navigation-overlay-content">
            <div class="overlay-controls">
                <VButton text class="nav-button" icon="pi pi-arrow-left"
                        @click="handleImageBack" :disabled="imageBackDisabled" />
                <div class="nav-count">
                    <i class="pi pi-image"></i>
                    {{ imageState.currentImageIndex + 1 }}
                    /
                    {{ imageState.images.length }}
                </div>
                <VButton text class="nav-button" icon="pi pi-arrow-right"
                        @click="handleImageNext" :disabled="imageNextDisabled" />
            </div>
        </div>
    </div>
</template>

<style scoped>
.navigation-overlay {
    position: fixed;
    bottom: 90px;
    width: 100%;
    background-color: var(--surface-section-transparent);
    z-index: 5;
    color: var(--primary-color);
    font-weight: 600;
    text-shadow: 1px 1px 2px var(--surface-section);
}

.navigation-overlay-content {
    display: flex;
    justify-content: space-between;
    max-width: 800px;
    margin: 0 auto;
}

.overlay-controls {
    display: flex;
    align-items: center;
    flex-basis: 100%;
    justify-content: center;
    max-width: 340px;
    margin: 0 auto;
}

.overlay-controls > * {
    flex-basis: 33%;
    text-align: center;
    margin: 0;
}

@media screen and (min-width: 340px) {
    .navigation-overlay {
        bottom: 100px;
        font-size: 1.2rem;
    }
}

@media screen and (min-width: 1200px) {
    .navigation-overlay-content {
        max-width: 1200px;
    }
}
</style>

<style>
.result-nav .navigation-overlay-content {
    margin-bottom: 10px;
}

.navigation-overlay .pi {
    text-shadow: 1px 1px 2px var(--surface-section);
}

.navigation-overlay .pi-image {
    bottom: -2px;
    position: relative;
}

.overlay-controls .p-button {
    padding: 12px 0;
}

@media screen and (min-width: 340px) {
    .navigation-overlay .pi {
        font-size: 1.25rem;
    }
}
</style>
