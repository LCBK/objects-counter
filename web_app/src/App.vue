<script setup lang="ts">
import { useViewStateStore } from "./stores/viewState";

const viewState = useViewStateStore();
</script>

<template>
    <header>

    </header>
    <main>
        <component :is="viewState.currentView"></component>
    </main>
</template>

<style scoped>
main {
    width: 100vw;
}
</style>
