<script setup lang="ts">
import VButton from "primevue/button";
import VDialog from "primevue/dialog";
import { useViewStateStore } from "../stores/viewState";
import { computed, onMounted, ref, watch } from "vue";


const visible = defineModel<boolean>();
const viewState = useViewStateStore();

const currentViewState = computed(() => viewState.currentStateName);
const isButtonAnimated = ref<Boolean>();

const props = defineProps({
    labeled: Boolean                // labeled with "Instruction" string and styled as a wider button
});


function animateButton() {
    setTimeout(() => {
        isButtonAnimated.value = true;
    }, 1000);
    setTimeout(() => {
        isButtonAnimated.value = false;
    }, 4000);
}

watch(currentViewState, async () => animateButton());

onMounted(() => animateButton());
</script>


<template>
    <VButton v-if="labeled" outlined id="instructions-button" icon="pi pi-info-circle" ref="button"
            @click="visible = true" label="Instructions" class="instructions-button-labeled" />
    <VButton v-else text rounded id="instructions-button" icon="pi pi-info-circle" ref="button"
            @click="visible = true" :class="{ animated: isButtonAnimated }" />
    <VDialog v-model:visible="visible" modal header="Instructions" id="instructions-popup" :dismissable-mask="true">
        <div v-if="currentViewState == 'beforeUpload'" class="instructions-text">
            <p>First off, take or upload a picture of the objects you want to count.</p>
            <p>To get the best results, follow these guidelines:</p>
            <ul>
                <li>Make sure the items are separated</li>
                <li>Provide appropriate lightning conditions (flat lightning, no sharp shadows)</li>
                <li>Make the background as uniform as possible</li>
            </ul>
            <p>Follow instructions given in the next steps for more help.</p>
        </div>
        <div v-else-if="currentViewState == 'editPoints'" class="instructions-text">
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
        <div v-else-if="currentViewState == 'confirmBackground'" class="instructions-text">
            <p>Your image has been processed and the background selected by the algorithm is highlighted on the preview.</p>
            <p>
                If the selection is correct, confirm your selection. Objects on the image will now get counted. <br>
                Otherwise, edit your selection by adjusting the points placed in the previous step.
            </p>
        </div>
        <div v-else-if="currentViewState == 'viewResult'" class="instructions-text">
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
    margin-top: 30px;
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
