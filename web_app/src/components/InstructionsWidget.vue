<script setup lang="ts">
import VButton from "primevue/button";
import VDialog from "primevue/dialog";
import { useViewStateStore, ViewStates } from "../stores/viewState";
import { computed, onMounted, ref, watch } from "vue";
import { useUserStateStore } from "@/stores/userState";


defineProps({
    labeled: Boolean                // labeled with "Instruction" string and styled as a wider button
});

const viewState = useViewStateStore();
const userState = useUserStateStore();

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
        <div v-if="currentViewState === ViewStates.MainView" class="instructions-text">
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
        <div v-else-if="currentViewState === ViewStates.ImageViewEditPoints" class="instructions-text">
            <p><b>Select the background</b> in your image that separates objects from one another.</p>
            <p>
                <b>Place points using the toolbar</b> below to indicate where the background is. <br>
                A single point or a few points will suffice, depending on background uniformity.
            </p>
            <p>
                To <b>include</b> a part of the image as the background, use <b>"positive" points</b>. <br>
                To <b>exclude</b> a part of the image from the background, use <b>"negative" points</b>.
            </p>
            <p>
                You will see the background selection immediately after placing the points. <br>
                If the selection is <b>satisfactory, proceed to the next step</b>.
            </p>
        </div>
        <div v-else-if="currentViewState === ViewStates.ImageViewCountingResult" class="instructions-text">
            <p>That's it!</p>
            <p>You can see the <b>element count on the bottom</b>.</p>
            <p>To see how many elements of <b>specific types</b> were counted, use the <b>"Details" button.</b></p>
            <p>
                If your result doesn't satisfy you, go back to the previous steps. <br>
                If there's no improvement, consider retaking the picture.
            </p>
            <p>
                You can also <b>rename the detected classifications</b> by tapping on them. <br>
                This will help you to better understand the results.
            </p>
            <p v-if="userState.isLoggedIn">
                This result has been saved to your user account.
                You can access it later in the <b>history</b> on your profile.
            </p>
        </div>
        <div v-else-if="currentViewState === ViewStates.ImageViewCreateDataset" class="instructions-text">
            <p>Elements found in your photo are now selected.</p>
            <p>
                To add the image to the dataset, <b>select one representant</b> of each category by tapping at them. <br>
                <i>(e.g. if you have 5 red pawns and 3 blue pawns, select one red and one blue pawn)</i>
            </p>
            <p>
                <b>If you have previously added an image</b> to this dataset, take care when selecting leaders.
                <b>Don't select representants of categories that were already selected</b> and classified in the previous images. <br>
                <i>(e.g. if there were 4 red pawns in the previous image, don't select a red pawn as a leader in this image)</i>
            </p>
            <p>When you're done, <b>submit your selection and proceed to the next step.</b></p>
        </div>
        <div v-else-if="currentViewState === ViewStates.ImageViewConfirmDataset" class="instructions-text">
            <p>
                The elements in this image were <b>classified based on the selected category representants</b>.
                If you have previously added images to this dataset, the classification will be based on these images as well.
            </p>
            <p>
                You can <b>add more images</b> to the dataset by tapping the "Add next image" button.
                You will go through the same process of selecting a background and category representants.
            </p>
            <p>
                <b>If the classification is incorrect, select "Adjust categories"</b>, tap the "Assign categories" button,
                select a category you want to assign elements to and tap boxes with elements you want to assign to this category.
            </p>
            <p>
                You can <b>rename the classifications in the "Adjust categories" mode</b> by tapping on their names.
            </p>
            <p>
                When you're done, tap the <b>"Create dataset" button, enter a fitting name and confirm</b>.
            </p>
        </div>
        <div v-else-if="currentViewState === ViewStates.ImageViewCompareWithDataset" class="instructions-text">
            <p>
                The elements in this image weren't classified, but only counted. <br>
                Their <b>classification will be based on the dataset</b> you're comparing with.
            </p>
            <p>
                The comparison will show you the <b>difference in the number of elements</b> (divided by categories)
                between the image and the dataset.
            </p>
            <p>
                You can <b>add more images</b> to the dataset by tapping the "Add next image" button.
                You will go through the same process of selecting a background and category representants.
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
    margin-top: 50px;
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
    text-align: left;
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
    text-align: left;
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

@media screen and (min-width: 340px) {
    #instructions-button {
        top: 80px;
        right: 10px;
    }

}

@media screen and (min-width: 400px) {
    #instructions-popup .instructions-text p,
    #instructions-popup .instructions-text li {
        font-size: 1rem;
    }
}

@media screen and (min-width: 788px) and (max-width: 1200px) {
    #instructions-button {
        right: calc(50vw - 768px / 2);
    }
}

@media screen and (min-width: 1220px) {
    #instructions-button {
        right: calc(50vw - 1200px / 2);
    }
}

</style>

<style>
#instructions-popup {
    max-width: 600px;
}

#instructions-button .pi {
    margin-right: 0 !important;
    font-size: 1.5rem;
    text-shadow: 0px 0px 6px var(--surface-ground);
}

#instructions-button.noShadow .pi {
    text-shadow: none;
    opacity: 0.4;
}

#instructions-popup .p-dialog-title {
    font-weight: 500;
    letter-spacing: 0.3px;
}

@media screen and (min-width: 340px) {
    #instructions-button .pi {
        font-size: 1.7rem;
    }
}
</style>
