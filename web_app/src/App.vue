<script setup lang="ts">
import { useSettingsStateStore } from "./stores/settingsState";
import { useUserStateStore } from "./stores/userState";
import { useViewStateStore } from "./stores/viewState";

const settingsState = useSettingsStateStore();
const userState = useUserStateStore();
const viewState = useViewStateStore();

settingsState.loadFromLocalStorage();
userState.loadFromCookies();

const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
mediaQuery.addEventListener("change", () => {
    settingsState.setThemeToPreferred();
});
</script>


<template>
    <main>
        <Transition name="view-fade" mode="out-in">
            <component :is="viewState.currentView"></component>
        </Transition>
    </main>
</template>


<style scoped>
.view-fade-enter-active, .view-fade-leave-active {
    transition: opacity .2s;
}

.view-fade-enter-from, .view-fade-leave-to {
    opacity: 0;
}

.view-fade-enter-to, .view-fade-leave-from {
    opacity: 1;
}

main {
    width: 100vw;
}
</style>
