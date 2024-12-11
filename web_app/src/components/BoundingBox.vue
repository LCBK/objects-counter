<script setup lang="ts">
import { boundingBoxColors } from '@/config';
import { useImageStateStore } from '@/stores/imageState';
import { useSettingsStateStore } from '@/stores/settingsState';
import { useViewStateStore, ViewStates } from '@/stores/viewState';
import { getClassificationBoxColor } from '@/utils';
import { computed } from 'vue';


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
        required: false
    },
    classificationName: {
        type: String,
        required: false
    }
});

const classification = computed(() => {
    if (props.classificationName) {
        return imageState.classifications.find(c => c.name === props.classificationName);
    }
    return undefined;
});

const boxColor = computed(() => {
    if (props.classificationName) {
        return getClassificationBoxColor(props.classificationName);
    }
    return boundingBoxColors[0];
});

const isSelectedAsLeader = computed(() => {
    return imageState.currentImage.selectedLeaderIds.includes(props.id)
        && (viewState.currentState === ViewStates.ImageViewSelectLeaders
            || viewState.currentState === ViewStates.ImageViewConfirmDataset
            || viewState.currentState === ViewStates.ImageViewConfirmCounting
        );
});

const selectedBoxColor = computed(() => {
    if (viewState.currentState === ViewStates.ImageViewSelectLeaders) {
        return boundingBoxColors[2];
    }
    else {
        return boxColor.value;
    }
});

const scale = computed(() => imageState.boundingBoxScale);

// CSS properties
const top = computed(() => props.topLeft[1] * scale.value + "px");
const left = computed(() => props.topLeft[0] * scale.value + "px");
const width = computed(() => (props.bottomRight[0] - props.topLeft[0]) * scale.value + "px");
const height = computed(() => (props.bottomRight[1] - props.topLeft[1]) * scale.value + "px");


function handleBoundingBoxClick() {
    // If creating dataset or counting with leaders, enable leader selection
    if (viewState.currentState === ViewStates.ImageViewSelectLeaders) {
        if (imageState.currentImage.selectedLeaderIds.includes(props.id)) {
            imageState.currentImage.selectedLeaderIds = imageState.currentImage.selectedLeaderIds.filter(id => id !== props.id);
        }
        else {
            imageState.currentImage.selectedLeaderIds.push(props.id);
        }
    }
    // If assigning classifications, enable assignment
    else if (viewState.currentState === ViewStates.ImageViewConfirmDataset && viewState.isAssigningClassifications) {
        if (!isSelectedAsLeader.value) {
            const element = imageState.currentImage.elements.find(el => el.id === props.id);

            if (element && element.classificationName !== undefined) {
                element.classificationName = viewState.currentlyAssignedClassificationName;
            }
        }
    }
}
</script>


<template>
    <div :class="(isSelectedAsLeader ? 'selected-box ' : '') + 'bounding-box'"
            v-bind:data-topleft="topLeft[0] + ',' + topLeft[1]"
            v-bind:data-bottomright="bottomRight[0] + ',' + bottomRight[1]"
            v-bind:data-certainty="certainty" v-bind:data-classification="classification"
            v-if="classification === undefined || classification.showBoxes"
            @click="handleBoundingBoxClick">
        <div>
            <div v-if="settingsState.showBoxCertainty && viewState.currentState !== ViewStates.ImageViewSelectLeaders" class="box-certainty">
                {{ certainty ? Math.round(certainty * 100) / 100 : "" }}
            </div>
            <div v-if="settingsState.showBoxLabel && viewState.currentState !== ViewStates.ImageViewSelectLeaders" class="box-classification">
                {{ classificationName }}
            </div>
            <div v-if="settingsState.showElementIds" class="box-ids">{{ id }}</div>
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

.selected-box .box-certainty,
.selected-box .box-ids,
.selected-box .box-classification {
    background-color: v-bind(selectedBoxColor);
}

@media screen and (min-width: 460px) {
    .bounding-box .box-certainty,
    .bounding-box .box-ids {
        font-size: 10px;
        line-height: 14px;
        bottom: -14px;
        right: -2px;
    }

    .bounding-box .box-classification {
        font-size: 10px;
        line-height: 14px;
        bottom: -14px;
        left: -2px;
    }
}

@media screen and (min-width: 768px) {
    .bounding-box .box-certainty,
    .bounding-box .box-ids {
        font-size: 12px;
        line-height: 16px;
        bottom: -16px;
        right: -2px;
    }

    .bounding-box .box-classification {
        font-size: 12px;
        line-height: 16px;
        bottom: -16px;
        left: -2px;
    }
}
</style>
