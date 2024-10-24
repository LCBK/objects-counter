<script setup lang="ts">
import { config, endpoints } from "@/config";
import { useImageStateStore } from "@/stores/imageState";
import { sendRequest, type Response } from "@/utils";
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

const isRenameDialogVisible = ref<boolean>(false);
const renameOldLabel = ref<string>("");
const renameNewLabel = ref<string>("");

const count = computed(() => imageState.objectClassifications[props.index].count);
const classificationName = computed(() => imageState.objectClassifications[props.index].classificationName);
const showBoxes = computed({
    get() {
        return imageState.objectClassifications[props.index].showBoxes;
    },
    set(value) {
        imageState.objectClassifications[props.index].showBoxes = value;
    }
});

function showRenameDialog(oldName: string) {
    renameOldLabel.value = oldName;
    renameNewLabel.value = oldName;
    isRenameDialogVisible.value = true;
}

function confirmRename() {
    let requestUri = config.serverUri + endpoints.renameClassification
            .replace("{result_id}", imageState.resultId.toString())
            .replace("{classification_name}", renameOldLabel.value);
    const requestData = renameNewLabel.value
    
    const responsePromise = sendRequest(requestUri, requestData, "POST");
    responsePromise.then(() => {
        imageState.objectClassifications[props.index].classificationName = renameNewLabel.value;
        isRenameDialogVisible.value = false;
    });
}
</script>


<template>
    <div class="quantity">
        <div class="quantity-count">{{ count }}</div>
        <div class="quantity-classification" @click="showRenameDialog(classificationName)">
            {{ /^\d*$/.test(classificationName) ? "Type " + classificationName : classificationName }}
        </div>
        <VInputSwitch class="quantity-switch" v-model="showBoxes" />
        <VDialog v-model:visible="isRenameDialogVisible" modal :dismissable-mask="true" :draggable="false"
                header="Change label" class="rename-dialog">
            <VInputText v-model="renameNewLabel" class="rename-input" :placeholder="renameOldLabel" />
            <div class="rename-controls">
                <VButton outlined label="Cancel" class="rename-cancel" @click="isRenameDialogVisible = false" />
                <VButton label="Rename" class="rename-rename" @click="confirmRename()" />
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

.quantity-classification {
    flex-basis: 60%;
    font-size: 1rem;
    font-weight: 300;
    letter-spacing: 0.3px;
    text-indent: 10px;
    cursor: pointer;
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
</style>
