<script setup lang="ts">
import { boundingBoxColors } from '@/config';
import { useImageStateStore } from '@/stores/imageState';
import { useSettingsStateStore } from '@/stores/settingsState';
import { ImageAction, useViewStateStore } from '@/stores/viewState';
import { computed, defineProps, ref } from 'vue';


const viewState = useViewStateStore();
const imageState = useImageStateStore();
const settingsState = useSettingsStateStore();

const props = defineProps({
    id: {
        type: Number,
        required: true
    },
    topLeft: {                          // top-left corner [x, y]
        type: Array<number>,
        required: true
    },
    bottomRight: {                      // bottom-right corner [x, y]
        type: Array<number>,
        required: true
    },
    certainty: {
        type: Number,
        required: true
    },
    classificationIndex: {
        type: Number,
        required: true
    }
});

const isSelected = ref<boolean>(false);

const boxColor = computed(() => {
    if (viewState.currentAction === ImageAction.CreateDataset) {
        return boundingBoxColors[0];
    }
    else {
        return imageState.objectClassifications[props.classificationIndex].boxColor;
    }
});
const selectedBoxColor = computed(() => boundingBoxColors[2]);
const classification = computed(() => imageState.objectClassifications[props.classificationIndex].classificationName);
const scale = computed(() => imageState.boundingBoxScale);

// CSS properties
const top = computed(() => props.topLeft[1] * scale.value + "px");
const left = computed(() => props.topLeft[0] * scale.value + "px");
const width = computed(() => (props.bottomRight[0] - props.topLeft[0]) * scale.value + "px");
const height = computed(() => (props.bottomRight[1] - props.topLeft[1]) * scale.value + "px");


function handleBoundingBoxClick() {
    // If creating dataset, enable leader selection
    if (viewState.currentAction === ImageAction.CreateDataset) {
        if (imageState.selectedLeaderIds.includes(props.id)) {
            imageState.selectedLeaderIds = imageState.selectedLeaderIds.filter(id => id !== props.id);
        }
        else {
            imageState.selectedLeaderIds.push(props.id);
        }
        isSelected.value = !isSelected.value;
    }
}
</script>


<template>
    <div :class="(isSelected ? 'selected-box ' : '') + 'bounding-box'"
            v-bind:data-topleft="props.topLeft[0] + ',' + props.topLeft[1]"
            v-bind:data-bottomright="props.bottomRight[0] + ',' + props.bottomRight[1]"
            v-bind:data-certainty="props.certainty" v-bind:data-classification="classification"
            v-if="imageState.objectClassifications[classificationIndex].showBoxes"
            @click="handleBoundingBoxClick">
        <div>
            <div v-if="settingsState.showBoxCertainty" class="box-certainty">{{ props.certainty }}</div>
            <div v-if="settingsState.showBoxLabel" class="box-classification">{{ classification }}</div>
            <div v-if="settingsState.showElementIds" class="box-ids">{{ props.id }}</div>
        </div>
        <div class="selected-box-overlay"></div>
    </div>
</template>


<style scoped>
.bounding-box {
    border-width: 2px;
    border-style: solid;
    border-color: v-bind(boxColor);
    position: absolute;
    left: v-bind(left);
    top: v-bind(top);
    width: v-bind(width);
    height: v-bind(height);
    transition: 0.3s border-color;
}

.bounding-box.selected-box {
    border-color: v-bind(selectedBoxColor);
}

.bounding-box .box-certainty,
.bounding-box .box-ids {
    background-color: v-bind(boxColor);
    position: absolute;
    line-height: 12px;
    bottom: -12px;
    right: -2px;
    font-size: 9px;
    font-weight: 700;
    color: white;
    padding: 0 3px;
}

.bounding-box .box-classification {
    background-color: v-bind(boxColor);
    position: absolute;
    line-height: 12px;
    bottom: -12px;
    left: -2px;
    font-size: 9px;
    font-weight: 700;
    color: white;
    padding: 0 3px;
    max-width: v-bind(width);
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
}

.selected-box-overlay {
    width: 100%;
    height: 100%;
    opacity: 0;
    background-color: v-bind(selectedBoxColor);
    transition: 0.2s opacity;
}

.selected-box .selected-box-overlay {
    opacity: 0.4;
}
</style>
