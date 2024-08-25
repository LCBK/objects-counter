<script setup lang="ts">
import VButton from "primevue/button";
import { useViewStateStore } from "@/stores/viewState";
import { useImageStateStore } from "@/stores/imageState";
import { config, endpoints } from "@/config";
import { sendRequest } from "@/utils";

const viewState = useViewStateStore();
const imageState = useImageStateStore();

function handleConfirmBackground() {
    const requestUri = config.serverUri + endpoints.acceptBackground.replace("{image_id}", imageState.imageId.toString());
    const requestData = JSON.stringify({});
    const responsePromise = sendRequest(requestUri, requestData, "POST");
    
    responsePromise.then((response) => {
        viewState.setState('viewResult');
        imageState.results = JSON.parse(response).data;
    });
}
</script>


<template>
    <div class="image-view-tool-bar bar">
        <VButton text label="Edit selection" class="edit-selection" icon="pi pi-pencil"
                @click="viewState.setState('editPoints')" />
        <VButton text label="Confirm selection" class="confirm-selection" icon="pi pi-check"
                @click="handleConfirmBackground" />
    </div>
</template>


<style scoped>
.image-view-tool-bar {
    padding: 0;
    position: fixed;
    bottom: 0;
    height: 90px;
    align-items: stretch;
}

.image-view-tool-bar > button {
    flex-direction: column;
    padding: 12px 1rem;
    justify-content: space-between;
    flex: 1 1 0px;
}
</style>
