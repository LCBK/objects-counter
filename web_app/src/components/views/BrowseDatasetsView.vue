<script setup lang="ts">
import VButton from "primevue/button";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import type { DatasetListItem } from "@/types/app";
import { base64ToImageUri } from "@/utils";
import SettingsWidget from "../SettingsWidget.vue";
import { onMounted, ref } from "vue";
import DatasetListItemComponent from "../DatasetListItem.vue";
import LoadingSpinner from "../LoadingSpinner.vue";
import { getDatasets, getDatasetsThumbnails } from "@/requests/datasets";



const viewState = useViewStateStore();

const userDatasets = ref<DatasetListItem[]>([]);


function onBack() {
    viewState.setState(ViewStates.UserView);
}

async function loadDatasets() {
    viewState.isWaitingForResponse = true;

    await getDatasets().then((response) => {
        userDatasets.value = [];
        for (const dataset of response) {
            userDatasets.value.push({
                id: dataset.id,
                name: dataset.name,
                timestamp: Date.parse(dataset.timestamp)
            } as DatasetListItem);
        }
    })

    await getDatasetsThumbnails().then((response) => {
        for (const item of response) {
            const datasetItem = userDatasets.value.find((datasetItem) => datasetItem.id == item.id) as DatasetListItem;
            if (datasetItem) {
                datasetItem.thumbnailUri = base64ToImageUri(item.thumbnail);
            }
        }

        viewState.isWaitingForResponse = false;
    });
}


onMounted(async () => {
    loadDatasets();
});
</script>


<template>
    <div id="browse-datasets-view" class="view">
        <div class="browse-datasets-view-nav-bar nav-bar bar">
            <div class="nav-bar-content bar-content">
                <VButton text rounded icon="pi pi-chevron-left" @click="onBack()" />
                <h2>Browse datasets</h2>
                <SettingsWidget />
            </div>
        </div>
        <p class="browse-datasets-notice notice">tap on a dataset to view details</p>
        <div class="browse-datasets-list">
            <DatasetListItemComponent v-for="(dataset, index) in userDatasets.sort((a, b) => b.timestamp - a.timestamp)"
                    :key="index" v-bind="dataset" @data-changed="loadDatasets" />
        </div>
        <p v-if="userDatasets.length === 0" class="notice">no items to show</p>
        <Transition name="waiting-overlay">
            <div v-if="viewState.isWaitingForResponse" class="waiting-overlay">
                <LoadingSpinner />
            </div>
        </Transition>
    </div>
</template>


<style scoped>
.browse-datasets-view-nav-bar h2 {
    color: var(--primary-color);
    font-size: 1.3rem;
    line-height: 38px;
    letter-spacing: 0.4px;
    font-weight: 600;
}

.browse-datasets-list {
    padding: 0 20px 8px 20px;
    max-height: calc(100vh - 91px);
    overflow-y: auto;
    max-width: 768px;
    margin: 0 auto;
}

.browse-datasets-list > *:not(:last-child) {
    border-bottom: 1px solid var(--surface-border);
}

.browse-datasets-notice {
    font-size: 0.8rem;
    text-align: center;
    margin: 63px 0 8px 0;
}

#browse-datasets-view .notice {
    text-align: center;
}

@media screen and (min-width: 340px) {
    .browse-datasets-view-nav-bar h2 {
        font-size: 1.4rem;
    }

    .browse-datasets-list {
        max-height: calc(100vh - 106px);
    }

    .browse-datasets-notice {
        margin-top: 78px;
    }
}

@media screen and (min-width: 380px) {
    .browse-datasets-view-nav-bar h2 {
        font-size: 1.5rem;
    }
}
</style>
