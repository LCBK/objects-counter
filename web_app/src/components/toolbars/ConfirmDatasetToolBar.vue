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
import { formatClassificationName, sendRequest } from "@/utils";
import InfoPopup from "../InfoPopup.vue";


const imageState = useImageStateStore();
const viewState = useViewStateStore();

const quantitiesVisible = ref<boolean>(false);
const datasetDialogVisible = ref<boolean>(false);
const datasetName = ref<string>("");
const classifications = computed(() => imageState.objectClassifications);
const assignedClassificationName = computed(() => {
    const name = imageState.objectClassifications[viewState.currentlyAssignedClassificationIndex].classificationName;
    return formatClassificationName(name);
});
const assignedBoxColor = computed(() => {
    return imageState.objectClassifications[viewState.currentlyAssignedClassificationIndex].boxColor;
});

const popupText = ref<string>("");
const popupHeader = ref<string>("");
const popupVisible = ref<boolean>(false);


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

        // These checks SHOULD never fail, so we don't need to show an error message
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
        popupText.value = "Failed to submit dataset";
        popupHeader.value = "Error";
        popupVisible.value = true;
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
            popupText.value = "Dataset created successfully";
            popupHeader.value = "Success";
            popupVisible.value = true;
        }
        else {
            popupText.value = "Failed to submit dataset";
            popupHeader.value = "Error";
            popupVisible.value = true;
        }
    });
}


function handleCreatedDataset() {
    window.setTimeout(() => {
        viewState.reset();
        imageState.reset();
    }, 500);
}
</script>


<template>
    <div class="image-view-tool-bar bar">
        <div class="bar-content tool-bar-content">
            <VButton text label="Adjust categories" icon="pi pi-list" @click="quantitiesVisible = true" />
            <div class="element-count">
                <span class="element-count-value">{{ imageState.imageElements.length }}</span>
                <span class="element-count-label">Elements</span>
            </div>
            <VButton text label="Submit dataset" icon="pi pi-check" @click="datasetDialogVisible = true" />
        </div>
    </div>
    <Transition name="fade">
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
    <VDialog v-model:visible="datasetDialogVisible" modal header="Submit dataset"
            class="dataset-dialog input-dialog" :dismissable-mask="true" :draggable="false">
        <label for="dataset-name" class="dataset-label">Dataset name</label>
        <VInputText v-model="datasetName" class="dataset-name" :autofocus="true" :inputId="'dataset-name'"
                placeholder="My board game" />
        <div class="dialog-controls">
            <VButton outlined label="Cancel" @click="datasetDialogVisible = false" />
            <VButton label="Submit" @click="submitDataset" />
        </div>
    </VDialog>
    <InfoPopup v-model="popupVisible" :text="popupText" :header="popupHeader"
            @close="handleCreatedDataset" :timeout="2500" />
</template>


<style scoped>
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
</style>

<style>
.quantities .p-sidebar-header {
    padding-bottom: 6px;
}

.change-categories .pi {
    margin-right: 8px;
}

@media screen and (min-width: 400px) {
    .change-categories .p-button-label {
        font-size: 1.1rem;
    }
}
</style>
