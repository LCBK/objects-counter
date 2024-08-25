<script setup lang="ts">
import VButton from "primevue/button";
import { useViewStateStore } from "@/stores/viewState";
import { config, endpoints } from "@/config";
import { useImageStateStore } from "@/stores/imageState";
import { createMaskImage, sendRequest } from "@/utils";
import { ref } from "vue";

const viewState = useViewStateStore();
const imageState = useImageStateStore();

const background = ref<HTMLImageElement>();

function handleConfirmPoints() {
    const pointPositions = imageState.points.map((point) => point.position);
    const requestUri = config.serverUri + endpoints.sendSelection.replace("{image_id}", imageState.imageId.toString());
    const requestData = JSON.stringify({ "data": pointPositions });
    const responsePromise = sendRequest(requestUri, requestData, "PUT");
    
    responsePromise.then((response) => {
        viewState.setState("confirmBackground");
        const maskImageData = createMaskImage(JSON.parse(response).mask);
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");
        if (ctx == undefined) return;
        ctx.canvas.width = imageState.width;
        ctx.canvas.height = imageState.height;
        ctx.putImageData(maskImageData, 0, 0);
        const maskImage = new Image();
        maskImage.onload = () => {
            ctx.drawImage(maskImage, 0, 0);
        };
        document.querySelector<HTMLImageElement>("#mask-image")!.src = canvas.toDataURL();        
    });
}
</script>


<template>
    <div class="image-view-tool-bar bar">
        <VButton text label="Add points" icon="pi pi-plus"
                @click="viewState.toggleAddPoint"
                :class="viewState.isAddingPoint ? 'active ' : '' + 'add-points'" />
        <VButton text label="Remove points" icon="pi pi-minus"
                @click="viewState.toggleRemovePoint"
                :class="viewState.isRemovingPoint ? 'active ' : '' + 'remove-points'" />
        <VButton text label="Confirm points" class="confirm-points" icon="pi pi-check"
                @click="handleConfirmPoints" />
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
