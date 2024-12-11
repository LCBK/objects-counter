<script setup lang="ts">
import { type DatasetClassificationListItem } from "@/types/app";
import {
    formatClassificationName,
    getClassificationsFromDataset,
    parseElementsToImage,
    processImageData
} from "@/utils";
import VDialog from "primevue/dialog";
import VButton from "primevue/button";
import VInputText from "primevue/inputtext";
import { ref } from "vue";
import { ImageAction, useViewStateStore, ViewStates } from "@/stores/viewState";
import { deleteDataset, getDataset, renameDataset } from "@/requests/datasets";
import { useImageStateStore } from "@/stores/imageState";
import { getImageBlob } from "@/requests/images";


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
const imageState = useImageStateStore();

const detailsVisible = ref<boolean>(false);
const renameDialogVisible = ref<boolean>(false);
const deleteDialogVisible = ref<boolean>(false);
const classifications = ref<DatasetClassificationListItem[]>([]);
const renameNewName = ref<string>("");

const date = new Date(props.timestamp).toISOString().split("T")[0];
const time = new Date(props.timestamp).toLocaleTimeString();


function showRenameDialog() {
    renameNewName.value = props.name;
    renameDialogVisible.value = true;
}

async function showDatasetDetails() {
    await getDataset(props.id).then(response => {
        classifications.value = getClassificationsFromDataset(response);
        classifications.value.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }));
        detailsVisible.value = true;
    });
}

async function handleShowDataset() {
    viewState.isWaitingForResponse = true;

    await getDataset(props.id).then(response => {
        imageState.datasetId = props.id;

        const promises = [] as Promise<void>[];
        for (const image of response.images) {
            promises.push(getImageBlob(image.id).then(blob => {
                processImageData(blob, image.id).then(() => {
                    parseElementsToImage(image.id, image.elements);
                });
            }));
        }

        Promise.all(promises).then(() => {
            viewState.currentAction = ImageAction.PreviewDataset;
            viewState.setState(ViewStates.ImageViewCountingResult);
            viewState.currentNavBarTitle = "Dataset preview";
        });
    }).finally(() => {
        viewState.isWaitingForResponse = false;
    });
}

async function handleRename() {
    await renameDataset(props.id, renameNewName.value).then(() => {
        emit("dataChanged");
        detailsVisible.value = false;
        renameDialogVisible.value = false;
    });
}

async function handleDelete() {
    deleteDataset(props.id).then(() => {
        emit("dataChanged");
        detailsVisible.value = false;
        deleteDialogVisible.value = false;
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
        <VButton v-if="viewState.currentState === ViewStates.ImageViewCompareWithDataset
                || viewState.currentState === ViewStates.ImageViewComparisonResult"
                label="Compare" class="compare-button" @click="$emit('compareClick', props.id)" />
        <div v-else class="details-controls">
            <VButton label="Rename" outlined @click="showRenameDialog" />
            <VButton label="Delete" outlined @click="deleteDialogVisible = true" />
            <VButton label="Show" @click="handleShowDataset" />
        </div>
    </VDialog>
    <VDialog v-model:visible="renameDialogVisible" modal :dismissable-mask="true" :draggable="false"
            header="Rename dataset" class="rename-dialog">
        <VInputText v-model="renameNewName" class="rename-input" :placeholder="name" :autofocus="true" />
        <div class="rename-controls">
            <VButton outlined label="Cancel" @click="renameDialogVisible = false" />
            <VButton label="Rename" @click="handleRename" />
        </div>
    </VDialog>
    <VDialog v-model:visible="deleteDialogVisible" modal :dismissable-mask="true" :draggable="false"
            header="Delete dataset" class="delete-dialog">
        <p>Are you sure you want to delete this dataset?</p>
        <div class="delete-controls">
            <VButton outlined label="Cancel" @click="deleteDialogVisible = false" />
            <VButton label="Delete" @click="handleDelete" />
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
    flex-wrap: wrap;
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
