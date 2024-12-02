<script setup lang="ts">
import { adjustClassifications } from "@/requests/datasets";
import { renameResultClassification } from "@/requests/results";
import { useImageStateStore } from "@/stores/imageState";
import { ImageAction, useViewStateStore } from "@/stores/viewState";
import { formatClassificationName, getBoxColorFromClassificationName } from "@/utils";
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

const count = computed(() => imageState.currentImage.classifications[props.index].count);
const name = computed(() => imageState.currentImage.classifications[props.index].name);
const boxColor = computed(() => getBoxColorFromClassificationName(name.value));
const showBoxes = computed({
    get() {
        return imageState.currentImage.classifications[props.index].showBoxes;
    },
    set(value) {
        imageState.currentImage.classifications[props.index].showBoxes = value;
    }
});
const isRenameDisabled = computed(() => {
    return (
        renameNewLabel.value === ""
        || renameNewLabel.value === renameOldLabel.value
        || imageState.currentImage.classifications.some((c) => c.name === renameNewLabel.value)
    );
});
const difference = computed(() => {
    return imageState.comparisonDifference[name.value];
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

async function confirmRename() {
    if (isRenameDisabled.value) return;

    if (viewState.currentAction === ImageAction.SimpleCounting) {
        // TODO: as results don't support multiple images yet, fix later
        await renameResultClassification(
            imageState.resultId, renameOldLabel.value, renameNewLabel.value
        ).then(() => {
            imageState.currentImage.classifications[props.index].name = renameNewLabel.value;
            isRenameDialogVisible.value = false;
        });
    }
    else {
        const oldName = imageState.currentImage.classifications[props.index].name;
        const changedImageIds = [] as number[];

        imageState.images.forEach((image) => {
            image.classifications.forEach((c) => {
                if (c.name === oldName) {
                    c.name = renameNewLabel.value;
                    if (!changedImageIds.includes(image.id)) {
                        changedImageIds.push(image.id);
                    }
                }
            });
        });

        changedImageIds.forEach((id) => {
            const image = imageState.images.find((i) => i.id === id);
            if (image) {
                const classifications = image.classifications.map((c) => {
                    return {
                        name: c.name,
                        elements: image.elements
                            .filter((el) => el.classificationIndex === c.index)
                            .map((el) => el.id)
                    };
                });

                adjustClassifications(imageState.datasetId, id, classifications);
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
