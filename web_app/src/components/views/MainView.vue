<script setup lang="ts">
import VButton from "primevue/button";
import ImageInput from "../ImageInput.vue";
import InstructionsWidget from "../InstructionsWidget.vue";
import LoadingSpinner from "../LoadingSpinner.vue";
import MainViewNavBar from "../navbars/MainViewNavBar.vue";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { checkServerStatus } from "@/utils";
import { onMounted, ref } from "vue";
import { config } from "@/config";

const viewState = useViewStateStore();

const isOffline = ref<boolean>(false);
const isOnline = ref<boolean>(false);
const isChecking = ref<boolean>(false);

function performServerCheck() {
    Promise.race([
        checkServerStatus(),
        new Promise((resolve) => setTimeout(() => resolve(false), config.serverIsAliveTimeout))
    ]).then((status) => {
        if (status) {
            isChecking.value = false;
            isOffline.value = false;
            isOnline.value = true;
        }
        else {
            isChecking.value = false;
            isOffline.value = true;
            isOnline.value = false;
        }
    });
}

function onRetry() {
    isChecking.value = true;
    performServerCheck();
}

onMounted(async () => {
    window.setTimeout(() => {
        if (isOnline.value) return;
        isChecking.value = true;
    }, config.serverIsAliveDelay);
    performServerCheck();
});
</script>


<template>
    <Transition name="status-fade" mode="out-in">
        <div v-if="isChecking" id="main-view" class="view server-checking">
            <h2>Checking server availability...</h2>
            <LoadingSpinner />
        </div>
        <div v-else-if="isOffline" id="main-view" class="view server-offline">
            <h2>Server Offline</h2>
            <p>The server is currently offline.<br>Please try again later.</p>
            <VButton class="debug-button wide-button" label="Retry" icon="pi pi-refresh" @click="onRetry()" />
        </div>
        <div v-else id="main-view" class="view">
            <MainViewNavBar />
            <ImageInput />
            <InstructionsWidget labeled />
            <VButton class="debug-button wide-button" outlined label="Debug functions" icon="pi pi-cog"
                    @click="viewState.setState(ViewStates.DebugView)" />
        </div>
    </Transition>
</template>


<style scoped>
.status-fade-enter-active, .status-fade-leave-active {
  transition: opacity .4s;
}

.status-fade-enter-from, .status-fade-leave-to {
  opacity: 0;
}

.status-fade-enter-to, .status-fade-leave-from {
    opacity: 1;
}

#main-view {
    width: 100vw;
    height: 100vh;          /* added for compatibility */
    height: 100dvh;
    display: flex;
    flex-direction: column;
    flex-wrap: nowrap;
    justify-content: center;
    margin: auto 0;
    text-align: center;
}

.debug-button {
    margin-top: 30px;
    align-self: center;
}

#main-view.server-checking {
    gap: 50px;
    align-items: center;
}

#main-view.server-checking h2 {
    max-width: 60%;
}

#main-view.server-offline {
    gap: 20px;
}

#main-view.server-offline h2 {
    color: var(--text-color);
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: 0.6px;
    margin-bottom: 10px;
}

#main-view.server-offline p {
    color: var(--text-color-secondary);
    font-size: 1rem;
    font-weight: 400;
    letter-spacing: 0.3px;
}

#main-view.server-offline .p-button {
    margin-top: 48px;
}
</style>

<style>
#main-view .p-button-label {
    font-weight: 600;
}

#main-view .debug-button .pi {
    font-size: 1.3rem;
}

#main-view.server-checking .loader {
    width: 80px;
    height: 80px;
}
</style>
