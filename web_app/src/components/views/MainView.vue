<script setup lang="ts">
import VButton from "primevue/button";
import VCheckbox from "primevue/checkbox";
import VDialog from "primevue/dialog";
import VInputText from "primevue/inputtext";
import ImageInput from "../ImageInput.vue";
import InstructionsWidget from "../InstructionsWidget.vue";
import LoadingSpinner from "../LoadingSpinner.vue";
import MainViewNavBar from "../navbars/MainViewNavBar.vue";
import { checkServerStatus } from "@/requests/other";
import { onMounted, ref } from "vue";
import { config } from "@/config";


// These are both used and initially set to false, because we want to show the main screen
// immediately after launching the app, as we are not sure if the server is online yet.
const isOnline = ref<boolean>(false);           // means that we are sure the server is online
const isOffline = ref<boolean>(false);          // means that we are sure the server is offline

const isCheckingStatus = ref<boolean>(false);
const receivedStatusResponse = ref<boolean>(false);
const serverAddressDialogVisible = ref<boolean>(false);
const serverAddress = ref<string>("");
const serverUseHttps = ref<boolean>(false);


function performServerCheck() {
    Promise.race([
        checkServerStatus(),
        new Promise(resolve => setTimeout(() => {
            resolve(false);
            receivedStatusResponse.value = true;
        }, config.serverIsAliveTimeout))
    ]).then(status => {
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

function handleRetry() {
    isCheckingStatus.value = true;
    performServerCheck();
}

function handleChangeAddress() {
    config.serverAddress = serverAddress.value;
    config.serverUseHttps = serverUseHttps.value;
    localStorage.setItem("serverAddress", serverAddress.value);
    localStorage.setItem("serverUseHttps", serverUseHttps.value.toString());

    serverAddressDialogVisible.value = false;
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
    <Transition name="fade" mode="out-in">
        <div v-if="isCheckingStatus" id="main-view" class="view server-checking">
            <h2>Checking server availability...</h2>
            <LoadingSpinner />
        </div>
        <div v-else-if="isOffline" id="main-view" class="view server-offline">
            <h2>Server Offline</h2>
            <p>The server is currently offline.<br>Please try again later.</p>
            <VButton class="wide-button" label="Retry" icon="pi pi-refresh" @click="handleRetry()" />
            <VButton class="wide-button" label="Change server address" icon="pi pi-pencil"
                    @click="serverAddressDialogVisible = true;" />
            <VDialog v-model:visible="serverAddressDialogVisible" modal header="Change address"
                    class="server-dialog input-dialog" :dismissable-mask="true" :draggable="false">
                <label for="server-address" class="server-label">Server address</label>
                <VInputText v-model="serverAddress" class="server-address" :autofocus="true"
                        :placeholder="config.serverAddress" :inputId="'server-address'" />
                <VCheckbox v-model="serverUseHttps" class="server-https" :inputId="'server-https'" binary />
                <label for="server-https" class="server-https-label">Use HTTPS</label>
                <div class="dialog-controls">
                    <VButton outlined label="Cancel" @click="serverAddressDialogVisible = false" />
                    <VButton label="Submit" @click="handleChangeAddress" />
                </div>
            </VDialog>
        </div>
        <div v-else id="main-view" class="view">
            <MainViewNavBar />
            <ImageInput />
            <InstructionsWidget labeled />
            <p class="notice">Reading recommended for better understanding</p>
        </div>
    </Transition>
</template>


<style scoped>
.server-dialog input {
    margin-bottom: 10px;
}

.server-dialog .server-https-label {
    position: relative;
    margin: 0 0 0 10px;
    top: 3px;
}

.server-dialog .dialog-controls {
    margin-top: 15px;
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
    margin-bottom: 64px;
}

#main-view.server-offline .wide-button {
    margin: 0 auto 10px auto;
}

#main-view .notice {
    max-width: 70%;
    margin: 10px auto 0 auto;
}

@media screen and (min-width: 340px) {
    #main-view.server-checking h2 {
        font-size: 1.5rem;
    }

    #main-view.server-offline h2 {
        font-size: 2.25rem;
    }

    #main-view.server-offline p {
        font-size: 1.125rem;
    }
}
</style>

<style>
#main-view.server-checking .loader {
    width: 80px;
    height: 80px;
}

@media screen and (min-width: 340px) {
    #main-view.server-checking .loader {
        width: 100px;
        height: 100px;
        border-width: 6px;
    }
}

@media screen and (min-width: 576px) {
    #main-view.server-checking .loader {
        width: 120px;
        height: 120px;
        border-width: 8px;
    }
}
</style>
