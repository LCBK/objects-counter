<script setup lang="ts">
import ImageDisplay from "../ImageDisplay.vue";
import ImageViewNavBar from "../navbars/ImageViewNavBar.vue";
import { useViewStateStore, ViewStates } from "../../stores/viewState";
import InstructionsViewWidget from "../InstructionsWidget.vue";
import { computed, ref } from "vue";

const viewState = useViewStateStore();

const isInfoCollapsed = ref<boolean>(false);
const additionalInfoBarClasses = computed(() => {
    const classes = [];

    if (isInfoCollapsed.value) {
        classes.push("info-collapsed");
    }
    if (viewState.isWaitingForResponse) {
        classes.push("info-waiting");
    }

    return classes.join(" ");
});
</script>


<template>
    <div id="image-view" class="view">
        <ImageViewNavBar />
        <div v-if="viewState.currentState === ViewStates.ImageViewCreateDataset ||
                viewState.currentState === ViewStates.ImageViewConfirmDataset"
                :class="additionalInfoBarClasses" id="additional-info-bar">
            <p v-if="viewState.currentState === ViewStates.ImageViewCreateDataset">
                Select one representant of each element category
            </p>
            <p v-else-if="viewState.currentState === ViewStates.ImageViewConfirmDataset">
                Adjust classifications or rename element categories
            </p>
            <InstructionsViewWidget />
            <div class="collapse-button" @click="isInfoCollapsed = !isInfoCollapsed">
                <i v-if="isInfoCollapsed" class="pi pi-angle-down"></i>
                <i v-else class="pi pi-angle-up"></i>
            </div>
        </div>
        <InstructionsViewWidget v-else />
        <ImageDisplay />
        <component :is="viewState.currentImageViewToolBar"></component>
    </div>
</template>


<style scoped>
#additional-info-bar {
    display: flex;
    width: 100%;
    position: absolute;
    top: 55px;
    background-color: var(--surface-section);
    transition: top 0.3s;
    z-index: 5;
}

#additional-info-bar p {
    padding: 10px 16px;
    width: 70%;
    color: var(--primary-color);
    line-height: 1.2rem;
    font-size: 0.9rem;
}

#additional-info-bar .collapse-button {
    color: var(--primary-color);
    position: absolute;
    bottom: -21px;
    left: 10%;
    transform: translateX(-50%);
    background-color: var(--surface-section);
    padding: 2px 10px 0px 10px;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
    font-size: 0.7rem;
    z-index: 100;
}

#additional-info-bar .collapse-button:hover {
    cursor: pointer;
}

#additional-info-bar.info-collapsed {
    top: -2px;
}

#additional-info-bar.info-waiting p,
#additional-info-bar.info-waiting .collapse-button i {
    opacity: 0.6;
}

@media screen and (max-width: 310px) {
    #additional-info-bar p {
        width: 85%;
    }
}
</style>

<style>
#additional-info-bar #instructions-button {
    position: relative;
    top: unset;
    right: unset;
    margin: auto;
    margin-right: 7px;
    transition: 0.1s;
}

#additional-info-bar.info-collapsed #instructions-button {
    opacity: 0;
}

#additional-info-bar:not(.info-collapsed) #instructions-button {
    transition-delay: 0.1s;
}

#additional-info-bar .collapse-button .pi {
    margin-right: 0;
}
</style>
