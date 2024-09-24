<script setup lang="ts">
import ImageInput from "../ImageInput.vue";
import InstructionsWidget from "../InstructionsWidget.vue";
import MainViewNavBar from "../navbars/MainViewNavBar.vue";
</script>


<template>
    <div id="main-view" class="view">
        <MainViewNavBar />
        <ImageInput />
        <InstructionsWidget labeled />
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
</style>

<style>
#main-view .p-button-label {
    font-weight: 600;
}
</style>
