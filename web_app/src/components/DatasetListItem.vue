<script setup lang="ts">
import { config, endpoints } from "@/config";
import { type DatasetClassificationListItem } from "@/types";
import { formatClassificationName, getClassificationsFromDataset, sendRequest } from "@/utils";
import VDialog from "primevue/dialog";
import VButton from "primevue/button";
import VInputText from "primevue/inputtext";
import { ref } from "vue";
import { useViewStateStore, ViewStates } from "@/stores/viewState";


const props = defineProps({
    id: {
        type: Number,
        required: true
    },
    name: {
        type: String,
        required: true
    },
    timestamp: {
        type: Number,
        required: true
    },
    thumbnailUri: {
        type: String,
        required: false
    }
});

const emit = defineEmits(["compareClick", "dataChanged"]);

const viewState = useViewStateStore();

const detailsVisible = ref<boolean>(false);
const renameDialogVisible = ref<boolean>(false);
const deleteDialogVisible = ref<boolean>(false);
const classifications = ref<DatasetClassificationListItem[]>([]);
const renameNewName = ref<string>("");

const date = new Date(props.timestamp).toISOString().split("T")[0];
const time = new Date(props.timestamp).toLocaleTimeString();


function showDatasetDetails() {
    const requestUri = config.serverUri + endpoints.getDataset.replace("{dataset_id}", props.id.toString());
    const requestPromise = sendRequest(requestUri, null, "GET");
    requestPromise.then((response) => {
        if (response.status === 200) {
            classifications.value = getClassificationsFromDataset(response.data);
            detailsVisible.value = true;
        }
        else {
            console.error("Failed to retrieve dataset details");
            return;
        }
    });
}

function showRenameDialog() {
    renameNewName.value = props.name;
    renameDialogVisible.value = true;
}

function confirmRename() {
    const requestUri = config.serverUri + endpoints.renameDataset.replace("{dataset_id}", props.id.toString());
    const requestData = JSON.stringify({ "name": renameNewName.value });
    const requestPromise = sendRequest(requestUri, requestData, "PATCH");
    requestPromise.then((response) => {
        if (response.status === 200) {
            emit("dataChanged");
            detailsVisible.value = false;
            renameDialogVisible.value = false;
        }
        else {
            console.error("Failed to rename dataset");
        }
    });
}

function confirmDelete() {
    const requestUri = config.serverUri + endpoints.deleteDataset.replace("{dataset_id}", props.id.toString());
    const requestPromise = sendRequest(requestUri, null, "DELETE");
    requestPromise.then((response) => {
        if (response.status === 204) {
            emit("dataChanged");
            detailsVisible.value = false;
            deleteDialogVisible.value = false;
        }
        else {
            console.error("Failed to delete dataset");
        }
    });
}
</script>


<template>
    <div class="dataset-item" @click="showDatasetDetails">
        <img :src="props.thumbnailUri" alt="No thumbnail" class="dataset-item-image" />
        <div>
            <div class="dataset-item-name">{{ name }}</div>
            <div class="dataset-item-date">{{ date }}</div>
            <div class="dataset-item-time">{{ time }}</div>
        </div>
    </div>
    <VDialog v-model:visible="detailsVisible" modal :dismissable-mask="true" :header="name"
            :draggable="false" class="dataset-details">
        <p class="dataset-details-date">{{ date }}, {{ time }}</p>
        <p class="dataset-classifications-label">Classified elements:</p>
        <div class="classification-list">
            <div v-for="(classification, index) in classifications" :key="index" class="classification-item">
                <div class="classification-count">{{ classification.count }}</div>
                <div class="classification-name">
                    {{ formatClassificationName(classification.name) }}
                </div>
            </div>
        </div>
        <VButton v-if="viewState.currentState === ViewStates.ImageViewCompareWithDataset"
                label="Compare" class="compare-button" @click="$emit('compareClick', props.id)" />
        <div v-else class="details-controls">
            <VButton label="Rename" outlined @click="showRenameDialog" />
            <VButton label="Delete" @click="deleteDialogVisible = true" />
        </div>
    </VDialog>
    <VDialog v-model:visible="renameDialogVisible" modal :dismissable-mask="true" :draggable="false"
            header="Rename dataset" class="rename-dialog">
        <VInputText v-model="renameNewName" class="rename-input" :placeholder="name" :autofocus="true" />
        <div class="rename-controls">
            <VButton outlined label="Cancel" @click="renameDialogVisible = false" />
            <VButton label="Rename" @click="confirmRename" />
        </div>
    </VDialog>
    <VDialog v-model:visible="deleteDialogVisible" modal :dismissable-mask="true" :draggable="false"
            header="Delete dataset" class="delete-dialog">
        <p>Are you sure you want to delete this dataset?</p>
        <div class="delete-controls">
            <VButton outlined label="Cancel" @click="deleteDialogVisible = false" />
            <VButton label="Delete" @click="confirmDelete" />
        </div>
    </VDialog>
</template>


<style scoped>
.dataset-item {
    display: flex;
    align-items: center;
    padding: 12px 0;
    user-select: none;
    cursor: pointer;
}

.dataset-item-name {
    font-weight: 500;
    font-size: 1rem;
    color: var(--text-color);
}

.dataset-item-date,
.dataset-item-time {
    font-weight: 500;
    font-size: 0.8rem;
    color: var(--text-color-secondary);
}

.dataset-item-image {
    height: 100%;
    border-radius: 8px;
    margin-right: 12px;
    max-width: 72px;
    max-height: 72px;
    aspect-ratio: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
}

.dataset-details-date {
    font-size: 0.9rem;
    line-height: 0.9rem;
    color: var(--text-color-secondary);
    margin-bottom: 20px;
}

.classification-list {
    display: flex;
    flex-direction: column;
    max-height: 65vh;
    overflow-y: auto;
}

.classification-item {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 2px;
}

.dataset-classifications-label {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-color);
    margin-bottom: 4px;
}

.classification-name {
    font-size: 0.9rem;
    color: var(--text-color);
}

.classification-count {
    font-size: 1.35rem;
    line-height: 1.9rem;
    font-weight: 600;
    color: var(--primary-color);
}

.compare-button {
    margin: 20px auto 0 auto;
    display: block;
}

.rename-input {
    margin-bottom: 12px;
}

.rename-controls,
.delete-controls,
.details-controls {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 12px;
}

@media screen and (min-width: 400px) {
    .dataset-item-name {
        font-size: 1.2rem;
    }

    .dataset-item-date,
    .dataset-item-time {
        font-size: 1rem;
    }

    .dataset-item-image {
        max-width: 96px;
        max-height: 96px;
    }

    .classification-name {
        font-size: 1rem;
    }

    .classification-count {
        font-size: 1.5rem;
        line-height: 2.1rem;
    }

    .dataset-details-date {
        font-size: 1rem;
        line-height: 1rem;
    }

    .dataset-classifications-label {
        font-size: 1.2rem;
    }

    .rename-controls,
    .delete-controls,
    .details-controls {
        gap: 16px;
        margin-top: 16px;
    }
}
</style>

<style>
.dataset-details {
    width: 95vw;
}

.dataset-details .p-dialog-header {
    padding-bottom: 2px;
}

.dataset-details .p-dialog-content {
    overflow: hidden;
}

.rename-dialog .p-dialog-header-icons,
.delete-dialog .p-dialog-header-icons {
    display: none;
}

.rename-dialog,
.delete-dialog,
.dataset-details {
    max-width: 400px;
}
</style>
