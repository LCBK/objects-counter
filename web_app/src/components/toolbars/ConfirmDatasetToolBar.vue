<script setup lang="ts">
import "./ImageViewToolBar.css";
import VButton from "primevue/button";
import VDialog from "primevue/dialog";
import VSidebar from "primevue/sidebar";
import VInputText from "primevue/inputtext";
import QuantitiesEntry from "../QuantitiesEntry.vue";
import { useImageStateStore } from "@/stores/imageState";
import { useViewStateStore } from "@/stores/viewState";
import { computed, ref, watch } from "vue";
import { config, endpoints } from "@/config";
import { sendRequest } from "@/utils";


const imageState = useImageStateStore();
const viewState = useViewStateStore();

const quantitiesVisible = ref<boolean>(false);
const datasetDialogVisible = ref<boolean>(false);
const datasetName = ref<string>("");
const classifications = computed(() => imageState.objectClassifications);
const assignedClassificationName = computed(() => {
    const name = imageState.objectClassifications[viewState.currentlyAssignedClassificationIndex].classificationName;
    return /^\d*$/.test(name) ? "Type " + name : name;
});
const assignedBoxColor = computed(() => {
    return imageState.objectClassifications[viewState.currentlyAssignedClassificationIndex].boxColor;
});


// Close quantities sidebar when user starts to assign classifications
watch(() => viewState.isSelectingAssignment, (newValue) => {
    if (!newValue) {
        quantitiesVisible.value = false;
    }
});


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
            console.log(requestData);
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
        <VButton text label="Adjust categories" icon="pi pi-list" @click="quantitiesVisible = true" />
        <div class="element-count">
            <span class="element-count-value">{{ imageState.imageElements.length }}</span>
            <span class="element-count-label">Elements</span>
        </div>
        <VButton text label="Submit dataset" icon="pi pi-check" @click="datasetDialogVisible = true" />
    </div>
    <Transition name="assign-fade">
        <div v-if="viewState.isAssigningClassifications" class="assignment-notice">
            <VButton text icon="pi pi-times" @click="viewState.isAssigningClassifications = false" />
            <div>
                <div class="assignment-notice-label">Currently assigning</div>
                <div class="assignment-notice-value">{{ assignedClassificationName }}</div>
            </div>
        </div>
    </Transition>
    <VSidebar v-model:visible="quantitiesVisible" position="bottom" style="height: auto"
            class="quantities" header="Counted elements" @hide="viewState.isSelectingAssignment = false">
        <VButton text label="Assign categories" icon="pi pi-pencil" class="change-categories"
                @click="viewState.isSelectingAssignment = true" />
        <div class="quantities-label-notice notice">You can toggle label visibility in the settings</div>
        <div class="quantities-header">
            <div class="quantities-col">Count</div>
            <div class="quantities-col">Label<span class="rename-notice notice">(tap to rename)</span></div>
            <div v-if="!viewState.isSelectingAssignment" class="quantities-col">Show boxes</div>
        </div>
        <div class="quantities-content">
            <QuantitiesEntry v-for="(quantity, index) in classifications" :key="index" :index="quantity.index" />
            <div v-if="classifications.length === 0" class="no-elements-notice notice">(no elements found)</div>
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
            <VButton label="Submit" @click="submitDataset" />
        </div>
    </VDialog>
</template>


<style scoped>
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

.change-categories {
    margin: 0 auto 5px auto;
    display: block;
    padding: 6px 12px;
}

.assignment-notice {
    display: flex;
    position: absolute;
    bottom: 120px;
    left: 10px;
}

.assignment-notice-label {
    font-size: 0.8rem;
    color: var(--text-color-secondary);
    line-height: 1.1rem;
}

.assignment-notice-value::before {
    content: "";
    width: 10px;
    height: 10px;
    background-color: v-bind(assignedBoxColor);
    display: inline-block;
    margin-right: 6px;
}

.assign-fade-enter-active, .assign-fade-leave-active {
    transition: opacity .2s;
}

.assign-fade-enter-from, .assign-fade-leave-to {
    opacity: 0;
}

.assign-fade-enter-to, .assign-fade-leave-from {
    opacity: 1;
}
</style>

<style>
.quantities .p-sidebar-header {
    padding-bottom: 6px;
}

.change-categories .pi {
    margin-right: 8px;
}
</style>
