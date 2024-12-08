<script setup lang="ts">
import { boundingBoxColors } from "@/config";
import { adjustClassifications } from "@/requests/datasets";
import { renameResultClassification } from "@/requests/results";
import { useImageStateStore } from "@/stores/imageState";
import { ImageAction, useViewStateStore } from "@/stores/viewState";
import { formatClassificationName, getClassificationBoxColor, getImageClassifications } from "@/utils";
import VButton from "primevue/button";
import VDialog from "primevue/dialog";
import VInputSwitch from "primevue/inputswitch";
import VInputText from "primevue/inputtext";
import { computed, ref } from "vue";


const props = defineProps({
    name: {
        type: String,
        required: true
    }
});

const imageState = useImageStateStore();
const viewState = useViewStateStore();

const isRenameDialogVisible = ref<boolean>(false);
const renameOldLabel = ref<string>("");
const renameNewLabel = ref<string>("");

const classification = computed(() => {
    return imageState.classifications.find(c => c.name === props.name);
});

const count = computed(() => {
    let count = 0;
    imageState.images.forEach(image => {
        count += image.elements.filter(el => el.classificationName === props.name).length;
    });
    return count
});

const boxColor = computed(() => {
    if (props.name) {
        return getClassificationBoxColor(props.name);
    }
    return boundingBoxColors[0];
});

const isRenameDisabled = computed(() => {
    return (
        renameNewLabel.value === ""
        || renameNewLabel.value === renameOldLabel.value
        || imageState.classifications.some(c => c.name === renameNewLabel.value)
    );
});

const difference = computed(() => {
    return imageState.comparisonDifference[props.name];
});

const diffClass = computed(() => {
    return difference.value > 0 ? "diff-positive" : difference.value < 0 ? "diff-negative" : '';
});


function handleAssignClick() {
    viewState.isSelectingAssignment = false;
    viewState.isAssigningClassifications = true;
    viewState.currentlyAssignedClassificationName = props.name;
}

function showRenameDialog(oldName: string) {
    renameOldLabel.value = oldName;
    renameNewLabel.value = oldName;
    isRenameDialogVisible.value = true;
}

async function confirmRename() {
    if (isRenameDisabled.value) return;

    const oldName = renameOldLabel.value;
    const newName = renameNewLabel.value;

    imageState.classificationRenameMap.forEach(mapping => {
        if (mapping.newName === oldName) mapping.newName = newName;
    });

    if (viewState.currentAction === ImageAction.SimpleCounting) {
        // TODO: as results don't support multiple images yet, fix later
        await renameResultClassification(
            imageState.resultId, oldName, newName
        ).then(() => {
            classification.value!.name = newName;
            imageState.images.forEach(image => {
                image.elements.forEach(el => {
                    if (el.classificationName === oldName) {
                        el.classificationName = newName;
                    }
                });
            });

            isRenameDialogVisible.value = false;
        });
    }
    else {
        const changedImageIds = [] as number[];

        imageState.classifications.forEach(c => {
            if (c.name === oldName) c.name = newName;
        });

        imageState.images.forEach(image => {
            image.elements.forEach(el => {
                if (el.classificationName === oldName) {
                    el.classificationName = newName;
                }
            });

            const imageClassifications = getImageClassifications(image.id);
            imageClassifications.forEach(c => {
                if (c.name === newName) {
                    if (!changedImageIds.includes(image.id)) {
                        changedImageIds.push(image.id);
                    }
                }
            });
        });

        changedImageIds.forEach(id => {
            const imageClassifications = getImageClassifications(id);
            const image = imageState.images.find(i => i.id === id);

            if (imageClassifications.length !== 0 && image) {
                const requestClassifications = imageClassifications.map(c => {
                    return {
                        name: c.name,
                        elements: image.elements
                            .filter(el => el.classificationName === c.name)
                            .map(el => el.id)
                    };
                });

                adjustClassifications(imageState.datasetId, id, requestClassifications);
            }
        });

        isRenameDialogVisible.value = false;
    }
}
</script>


<template>
    <div :class="(imageState.images.length > 1 ? 'quantity-multiple ' : '') + 'quantity'">
        <div :class="(viewState.currentAction === ImageAction.CompareWithDataset ? 'diff ' : '') + 'quantity-count'">
            {{ count }}
            <span v-if="viewState.currentAction === ImageAction.CompareWithDataset" :class="'diff-value ' + diffClass">
                ({{ difference }})
            </span>
        </div>
        <div class="quantity-classification" @click="showRenameDialog(name)">
            {{ formatClassificationName(name) }}
        </div>
        <VInputSwitch v-if="!viewState.isSelectingAssignment" class="quantity-switch" v-model="classification!.showBoxes" />
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
    background-color: v-bind(boxColor);
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
