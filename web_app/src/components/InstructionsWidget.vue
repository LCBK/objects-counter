<script setup lang="ts">
import VButton from "primevue/button";
import VDialog from "primevue/dialog";
import { useViewStateStore, ViewStates } from "../stores/viewState";
import { computed, onMounted, ref, watch } from "vue";


const props = defineProps({
    labeled: Boolean                // labeled with "Instruction" string and styled as a wider button
});

const viewState = useViewStateStore();

const visible = defineModel<boolean>();
const currentViewState = computed(() => viewState.currentState);
const isButtonAnimated = ref<Boolean>();


function animateButton() {
    setTimeout(() => {
        isButtonAnimated.value = true;
    }, 1000);
    setTimeout(() => {
        isButtonAnimated.value = false;
    }, 4000);
}


watch(currentViewState, async () => {
    animateButton();
    visible.value = false;
});

onMounted(() => animateButton());
</script>


<template>
    <VButton v-if="labeled" outlined id="instructions-button" icon="pi pi-info-circle" ref="button"
            @click="visible = true" label="Instructions" class="instructions-button-labeled wide-button" />
    <VButton v-else text rounded id="instructions-button" icon="pi pi-info-circle" ref="button"
            @click="visible = true" :class="{ animated: isButtonAnimated, noShadow: viewState.isWaitingForResponse }" />
    <VDialog v-model:visible="visible" modal header="Instructions" class="popup" id="instructions-popup" :dismissable-mask="true">
        <div v-if="currentViewState == ViewStates.MainView" class="instructions-text">
            <p>First off, take or upload a picture of the objects you want to count.</p>
            <p>To get the best results, follow these guidelines:</p>
            <ul>
                <li>Make sure the items are separated</li>
                <li>Provide appropriate lightning conditions (flat lightning, no sharp shadows)</li>
                <li>Make the background as uniform as possible</li>
            </ul>
            <p>Follow instructions given in the next steps for more help.</p>
            <p>You can also sign in to compare different results and track your history.</p>
        </div>
        <div v-else-if="currentViewState == ViewStates.ImageEditPoints" class="instructions-text">
            <p>Select the background in your image that separates objects from one another.</p>
            <p>
                Place points using the toolbar below to indicate where the background is. <br>
                A single point or a few points will suffice, depending on background uniformity.
            </p>
            <p>
                To include a part of the image as the background, use "positive" points. <br>
                To exclude a part of the image from the background, use "negative" points.
            </p>
        </div>
        <div v-else-if="currentViewState == ViewStates.ImageViewResult" class="instructions-text">
            <p>That's it!</p>
            <p>You can see the element count on the bottom.</p>
            <p>To see how many elements of specific types were counted, use the "Details" button.</p>
            <p>
                If your result doesn't satisfy you, go back to the previous steps. <br>
                If there's no improvement, consider retaking the picture.
            </p>
        </div>
    </VDialog>
</template>


<style scoped>
#instructions-button {
    position: absolute;
    top: 65px;
    right: 8px;
    z-index: 200;
}

#instructions-button.instructions-button-labeled {
    position: relative;
    top: 0;
    right: 0;
    margin-top: 40px;
    width: 90%;
    max-width: 240px;
    height: 50px;
    align-self: center;
}

#instructions-button span {
    margin: 0;
}

#instructions-button.animated {
    animation: pulse-animation 1s infinite linear;
}

#instructions-popup .instructions-text {
    font-weight: 400;
    letter-spacing: 0.2px;
}

#instructions-popup .instructions-text p {
    margin: 12px 0;
    font-size: 0.9rem;
}

#instructions-popup .instructions-text p:last-child {
    margin-bottom: 0;
}

#instructions-popup .instructions-text ul {
    padding-left: 25px;
}

#instructions-popup .instructions-text li {
    margin: 4px 0;
    font-size: 0.9rem;
}

@keyframes pulse-animation {
    0% {
        background-color: rgba(96, 165, 250, 0.0);
        box-shadow: 0 0 0 0 rgba(96, 165, 250, 0.0);
    }
    50% {
        background-color: rgba(96, 165, 250, 0.2);
        box-shadow: 0 0 0 6px rgba(96, 165, 250, 0.2);
    }
    100% {
        background-color: rgba(96, 165, 250, 0.0);
        box-shadow: 0 0 0 12px rgba(96, 165, 250, 0.0);
    }
}
</style>

<style>
#instructions-button .pi {
    margin-right: 0 !important;
    font-size: 1.5rem;
    text-shadow: 0px 0px 6px var(--surface-ground);
}

#instructions-button.noShadow .pi {
    text-shadow: none;
    opacity: 0.4;
}

#main-view #instructions-button .pi {
    font-size: 1.3rem;
}

#instructions-popup .p-dialog-title {
    font-weight: 500;
    letter-spacing: 0.3px;
}
</style>
