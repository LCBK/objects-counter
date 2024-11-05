<script setup lang="ts">
import VButton from "primevue/button";
import ImageInput from "../ImageInput.vue";
import InstructionsWidget from "../InstructionsWidget.vue";
import LoadingSpinner from "../LoadingSpinner.vue";
import MainViewNavBar from "../navbars/MainViewNavBar.vue";
import { checkServerStatus } from "@/utils";
import { onMounted, ref } from "vue";
import { config } from "@/config";


// These are both used and initially set to false, because we want to show the main screen
// immediately after launching the app, as we are not sure if the server is online yet.
const isOnline = ref<boolean>(false);           // means that we are sure the server is online
const isOffline = ref<boolean>(false);          // means that we are sure the server is offline

const isCheckingStatus = ref<boolean>(false);
const receivedStatusResponse = ref<boolean>(false);


function performServerCheck() {
    Promise.race([
        checkServerStatus(),
        new Promise((resolve) => setTimeout(() => {
            resolve(false);
            receivedStatusResponse.value = true;
        }, config.serverIsAliveTimeout))
    ]).then((status) => {
        if (status) {
            isOffline.value = false;
            isOnline.value = true;
        }
        else {
            isOffline.value = true;
            isOnline.value = false;
        }
        receivedStatusResponse.value = true;
        isCheckingStatus.value = false;
    });
}

function onRetry() {
    isCheckingStatus.value = true;
    performServerCheck();
}


onMounted(async () => {
    performServerCheck();
    window.setTimeout(() => {
        if (isOnline.value || receivedStatusResponse.value) return;
        isCheckingStatus.value = true;
    }, config.serverIsAliveDelay);
});
</script>


<template>
    <Transition name="status-fade" mode="out-in">
        <div v-if="isCheckingStatus" id="main-view" class="view server-checking">
            <h2>Checking server availability...</h2>
            <LoadingSpinner />
        </div>
        <div v-else-if="isOffline" id="main-view" class="view server-offline">
            <h2>Server Offline</h2>
            <p>The server is currently offline.<br>Please try again later.</p>
            <VButton class="wide-button" label="Retry" icon="pi pi-refresh" @click="onRetry()" />
        </div>
        <div v-else id="main-view" class="view">
            <MainViewNavBar />
            <ImageInput />
            <InstructionsWidget labeled />
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
#main-view.server-checking .loader {
    width: 80px;
    height: 80px;
}
</style>
