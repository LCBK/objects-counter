<script setup lang="ts">
import "./ImageViewToolBar.css";
import VButton from "primevue/button";
import VSidebar from "primevue/sidebar";
import QuantitiesEntry from "../QuantitiesEntry.vue";
import ImageNavigationOverlay from "../ImageNavigationOverlay.vue";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { ref } from "vue";


const imageState = useImageStateStore();
const viewState = useViewStateStore();

const quantitiesVisible = ref<boolean>(false);


function handleReturnClick() {
    viewState.setState(ViewStates.ImageEditPoints);
    viewState.showBackground = true;
    viewState.isEditingExistingResult = true;
    imageState.clearAllResults();
}
</script>


<template>
    <div class="image-view-tool-bar bar">
        <div class="bar-content tool-bar-content">
            <VButton text label="Adjust" icon="pi pi-pencil" @click="handleReturnClick();" />
            <div class="element-count">
                <span class="element-count-value">{{ imageState.currentImage.elements.length }}</span>
                <span class="element-count-label">Elements</span>
            </div>
            <VButton text label="Details" icon="pi pi-list" @click="quantitiesVisible = true" />
        </div>
    </div>
    <ImageNavigationOverlay v-if="imageState.images.length > 1" />
    <VSidebar v-model:visible="quantitiesVisible" position="bottom" style="height: auto" class="quantities" header="Counted elements">
        <div class="quantities-label-notice notice">You can toggle label visibility in the settings</div>
        <div class="quantities-header">
            <div class="quantities-col">Count</div>
            <div class="quantities-col">Label<span class="rename-notice notice">(tap to rename)</span></div>
            <div class="quantities-col">Show boxes</div>
        </div>
        <div class="quantities-content">
            <QuantitiesEntry v-for="(classification, index) in imageState.classifications"
                    :key="index" :name="classification.name" />
            <div v-if="imageState.classifications.length === 0" class="no-elements-notice notice">
                (no elements found)
            </div>
        </div>
    </VSidebar>
</template>
