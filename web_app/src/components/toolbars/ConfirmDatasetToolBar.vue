<script setup lang="ts">
import "./ImageViewToolBar.css";
import VButton from "primevue/button";
import VDialog from "primevue/dialog";
import VSidebar from "primevue/sidebar";
import VInputText from "primevue/inputtext";
import QuantitiesEntry from "../QuantitiesEntry.vue";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore } from "@/stores/viewState";
import { computed, ref } from "vue";
import { config, endpoints } from "@/config";
import { sendRequest } from "@/utils";


const imageState = useImageStateStore();
const viewState = useViewStateStore();

const quantitiesVisible = ref<boolean>(false);
const datasetDialogVisible = ref<boolean>(false);
const datasetName = ref<string>("");
const classifications = computed(() => imageState.objectClassifications);


function handleSubmitDatasetClick() {
    submitDataset();
}


function submitDataset() {
    const classifications = imageState.objectClassifications.map((classification) => {
        const elements = imageState.imageElements.filter((el) => el.classificationIndex === classification.index)
        const elementIds = elements.map((el) => el.id);
        const leaders = elements.filter((el) => el.isLeader);

        if (leaders.length === 0) {
            console.error("No leader found for classification " + classification.classificationName);
            return null;
        }
        else if (leaders.length > 1) {
            console.error("Multiple leaders found for classification " + classification.classificationName);
            return null;
        }

        return {
            name: classification.classificationName,
            leader: leaders[0].id,
            elements: elementIds
        };
    });
    if (classifications.some((classification) => classification === null)) {
        console.error("Failed to submit dataset");
        return;
    }

    const requestUri = config.serverUri + endpoints.createDataset;
    const requestData = JSON.stringify({
        name: datasetName.value,
        image_id: imageState.imageId,
        classifications: classifications
    });

    const requestPromise = sendRequest(requestUri, requestData, "POST");
    requestPromise.then((response) => {
        if (response.status === 200) {
            console.log("Dataset submitted successfully");
            // TODO: handle response (same as registration popup)
            imageState.reset();
            viewState.reset();
        }
        else {
            console.error("Failed to submit dataset");
        }
    });
}
</script>


<template>
    <div class="image-view-tool-bar bar">
        <VButton text label="Details" icon="pi pi-list" @click="quantitiesVisible = true" />
        <div class="element-count">
            <span class="element-count-value">{{ imageState.imageElements.length }}</span>
            <span class="element-count-label">Elements</span>
        </div>
        <VButton text label="Submit dataset" icon="pi pi-check" @click="datasetDialogVisible = true" />
    </div>
    <VSidebar v-model:visible="quantitiesVisible" position="bottom" style="height: auto" class="quantities" header="Counted elements">
        <div class="quantities-label-notice">You can toggle label visibility in the settings</div>
        <div class="quantities-header">
            <div class="quantities-col">Count</div>
            <div class="quantities-col">Label<span class="rename-notice">(tap to rename)</span></div>
            <div class="quantities-col">Show boxes</div>
        </div>
        <div class="quantities-content">
            <QuantitiesEntry v-for="(quantity, index) in classifications" :key="index" :index="quantity.index" />
            <div v-if="classifications.length === 0" class="no-elements-notice">(no elements found)</div>
        </div>
    </VSidebar>
    <VDialog v-model:visible="datasetDialogVisible" modal header="Submit dataset" class="dataset-dialog"
            :dismissable-mask="true" :draggable="false">
        <p><span>{{ imageState.selectedLeaderIds.length }}</span> categories detected</p>
        <label for="dataset-name" class="dataset-label">Dataset name</label>
        <VInputText v-model="datasetName" class="dataset-name" :autofocus="true" :inputId="'dataset-name'"
                placeholder="My board game" />
        <div class="dialog-controls">
            <VButton outlined label="Cancel" @click="datasetDialogVisible = false" />
            <VButton label="Submit" @click="handleSubmitDatasetClick" />
        </div>
    </VDialog>
</template>


<style scoped>
.rename-notice,
.no-elements-notice {
    margin-left: 10px;
    color: var(--text-color-secondary);
    opacity: 0.7;
}

.no-elements-notice {
    margin: 20px 0 10px 0;
    text-align: center;
}

.dataset-dialog input {
    margin-bottom: 30px;
    width: 100%;
}

.dataset-dialog p {
    user-select: none;
    line-height: 1.8rem;
}

.dataset-dialog span {
    font-weight: 600;
    font-size: 1.4rem;
    margin-right: 2px;
}

.dataset-dialog label {
    display: inline-block;
    margin-bottom: 8px;
    margin-top: 16px;
    color: var(--text-color-secondary);
    user-select: none;
}

.dataset-dialog .dialog-controls {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}
</style>
