<script setup lang="ts">
import { useSettingsStateStore } from "./stores/settingsState";
import { useUserStateStore } from "./stores/userState";
import { useViewStateStore } from "./stores/viewState";

const settingsState = useSettingsStateStore();
const userState = useUserStateStore();
const viewState = useViewStateStore();

settingsState.loadFromLocalStorage();
settingsState.loadSavedServerAddress();
userState.loadFromCookies();

const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
mediaQuery.addEventListener("change", () => {
    settingsState.setThemeToPreferred();
});
</script>


<template>
    <main>
        <Transition name="fade" mode="out-in">
            <component :is="viewState.currentView"></component>
        </Transition>
    </main>
</template>


<style scoped>
main {
    width: 100vw;
}
</style>
