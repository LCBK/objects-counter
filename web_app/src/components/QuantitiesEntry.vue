<script setup lang="ts">
import { config, endpoints } from "@/config";
import { useImageStateStore } from "@/stores/imageState";
import { ImageAction, useViewStateStore } from "@/stores/viewState";
import { formatClassificationName, sendRequest } from "@/utils";
import VButton from "primevue/button";
import VDialog from "primevue/dialog";
import VInputSwitch from "primevue/inputswitch";
import VInputText from "primevue/inputtext";
import { computed, ref } from "vue";

// This component will change imageState, it will update its parents.
// That's why we have only an index prop, which we use to access and update object classification properties.

const props = defineProps({
    index: {
        type: Number,
        required: true
    }
});

const imageState = useImageStateStore();
const viewState = useViewStateStore();

const isRenameDialogVisible = ref<boolean>(false);
const renameOldLabel = ref<string>("");
const renameNewLabel = ref<string>("");

const count = computed(() => imageState.objectClassifications[props.index].count);
const classificationName = computed(() => imageState.objectClassifications[props.index].classificationName);
const classificationBoxColor = computed(() => imageState.objectClassifications[props.index].boxColor);
const showBoxes = computed({
    get() {
        return imageState.objectClassifications[props.index].showBoxes;
    },
    set(value) {
        imageState.objectClassifications[props.index].showBoxes = value;
    }
});
const isRenameDisabled = computed(() => {
    return (
        renameNewLabel.value === ""
        || renameNewLabel.value === renameOldLabel.value
        || imageState.objectClassifications.some((c) => c.classificationName === renameNewLabel.value)
    );
});
const difference = computed(() => {
    return imageState.comparisonDifference[classificationName.value as any];
});
const diffClass = computed(() => {
    return difference.value > 0 ? "diff-positive" : difference.value < 0 ? "diff-negative" : '';
});


function handleAssignClick() {
    viewState.isSelectingAssignment = false;
    viewState.isAssigningClassifications = true;
    viewState.currentlyAssignedClassificationIndex = props.index;
}

function showRenameDialog(oldName: string) {
    renameOldLabel.value = oldName;
    renameNewLabel.value = oldName;
    isRenameDialogVisible.value = true;
}

function confirmRename() {
    if (isRenameDisabled.value) return;

    // Classifications are final and stored on the server, so the app requests a rename from the server.
    if (viewState.currentAction !== ImageAction.CreateDataset) {
        let requestUri = config.serverUri + endpoints.renameClassification
                .replace("{result_id}", imageState.resultId.toString())
                .replace("{classification_name}", renameOldLabel.value);
        const requestData = renameNewLabel.value

        const responsePromise = sendRequest(requestUri, requestData, "POST");
        responsePromise.then((response) => {
            if (response.status === 200) {
                imageState.objectClassifications[props.index].classificationName = renameNewLabel.value;
            }
            else {
                console.error("Failed to rename classification");
            }
            isRenameDialogVisible.value = false;
        });
    }
    // When creating a dataset, classifications are final when confirming the dataset, rename locally.
    else {
        imageState.objectClassifications[props.index].classificationName = renameNewLabel.value;
        isRenameDialogVisible.value = false;
    }
}
</script>


<template>
    <div class="quantity">
        <div :class="(viewState.currentAction === ImageAction.CompareWithDataset ? 'diff ' : '') + 'quantity-count'">
            {{ count }}
            <span v-if="viewState.currentAction === ImageAction.CompareWithDataset" :class="'diff-value ' + diffClass">
                ({{ difference }})
            </span>
        </div>
        <div class="quantity-classification" @click="showRenameDialog(classificationName)">
            {{ formatClassificationName(classificationName) }}
        </div>
        <VInputSwitch v-if="!viewState.isSelectingAssignment" class="quantity-switch" v-model="showBoxes" />
        <VButton v-else class="assign-button" label="Assign" @click="handleAssignClick" />
        <VDialog v-model:visible="isRenameDialogVisible" modal :dismissable-mask="true" :draggable="false"
                header="Change label" class="rename-dialog">
            <VInputText v-model="renameNewLabel" class="rename-input" :placeholder="renameOldLabel" :autofocus="true" />
            <div class="rename-controls">
                <VButton outlined label="Cancel" class="rename-cancel" @click="isRenameDialogVisible = false" />
                <VButton label="Rename" class="rename-rename" @click="confirmRename()" :disabled="isRenameDisabled" />
            </div>
        </VDialog>
    </div>
</template>


<style scoped>
.quantity {
    display: flex;
    padding-bottom: 3px;
    align-items: center;
}

.quantity:not(:first-child) {
    padding-top: 3px;
    border-top: 1px solid var(--surface-border);
}

.quantity-count {
    flex-basis: 15%;
    font-size: 1.6rem;
    font-weight: 500;
    text-indent: 0;
    text-align: center;
}

.quantity-count.diff {
    flex-basis: 20%;
}

.quantity-classification {
    flex-basis: 60%;
    font-size: 1rem;
    font-weight: 300;
    letter-spacing: 0.3px;
    text-indent: 10px;
    cursor: pointer;
}

.quantity-classification::before {
    content: "";
    width: 10px;
    height: 10px;
    background-color: v-bind(classificationBoxColor);
    display: inline-block;
    margin-right: 6px;
}

.quantity-switch {
    flex-basis: 25%;
}

.rename-input {
    margin-bottom: 24px;
}

.rename-controls {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

.assign-button {
    padding: 5px 10px;
    font-size: 0.85rem;
}

.diff-value {
    font-size: 0.9rem;
    font-weight: 400;
}

.diff-positive {
    color: var(--color-success);
}

.diff-negative {
    color: var(--color-error);
}
</style>
