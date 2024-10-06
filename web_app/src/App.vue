<script setup lang="ts">
import { useUserStateStore } from "./stores/userState";
import { useViewStateStore } from "./stores/viewState";

const viewState = useViewStateStore();
viewState.setThemeToPreferred();

const userState = useUserStateStore();
userState.loadFromCookies();

const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
mediaQuery.addEventListener("change", () => {
    viewState.setThemeToPreferred();
});
</script>


<template>
    <main>
        <component :is="viewState.currentView"></component>
    </main>
</template>


<style scoped>
main {
    width: 100vw;
}
</style>
