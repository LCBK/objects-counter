<script setup lang="ts">
import { config } from "./config";
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

// If server address was stored in local storage, use it
if (localStorage.getItem("serverAddress")) {
    config.serverAddress = localStorage.getItem("serverAddress") as string;
}

if (localStorage.getItem("serverUseHttps")) {
    config.serverUseHttps = localStorage.getItem("serverUseHttps") === "true";
}
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
