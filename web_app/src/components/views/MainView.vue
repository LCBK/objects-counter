<script setup lang="ts">
import VButton from "primevue/button";
import ImageInput from "../ImageInput.vue";
import InstructionsWidget from "../InstructionsWidget.vue";
import MainViewNavBar from "../navbars/MainViewNavBar.vue";
import { useViewStateStore, ViewStates } from "@/stores/viewState";

const viewState = useViewStateStore();
</script>


<template>
    <div id="main-view" class="view">
        <MainViewNavBar />
        <ImageInput />
        <InstructionsWidget labeled />
        <VButton class="debug-button wide-button" outlined label="Debug functions" icon="pi pi-cog"
                @click="viewState.setState(ViewStates.DebugView)" />
    </div>
</template>


<style scoped>
#main-view {
    width: 100vw;
    height: 100vh;          /* added for compatibility */
    height: 100dvh;
    display: flex;
    flex-direction: column;
    flex-wrap: nowrap;
    justify-content: center;
    margin: auto 0;
}

.debug-button {
    margin-top: 30px;
    align-self: center;
}
</style>

<style>
#main-view .p-button-label {
    font-weight: 600;
}

#main-view .debug-button .pi {
    font-size: 1.3rem;
}
</style>
