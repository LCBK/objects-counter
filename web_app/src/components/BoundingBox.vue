<script setup lang="ts">
import { useImageStateStore } from '@/stores/imageState';
import { useViewStateStore } from '@/stores/viewState';
import { computed, defineProps } from 'vue';


const imageState = useImageStateStore();
const viewState = useViewStateStore();
const props = defineProps({
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

const boxColor = computed(() => imageState.objectClassifications[props.classificationIndex].boxColor);
const classification = computed(() => imageState.objectClassifications[props.classificationIndex].classificationName);
const scale = computed(() => imageState.boundingBoxScale);

// CSS properties
const top = computed(() => props.topLeft[1] * scale.value + "px");
const left = computed(() => props.topLeft[0] * scale.value + "px");
const width = computed(() => (props.bottomRight[0] - props.topLeft[0]) * scale.value + "px");
const height = computed(() => (props.bottomRight[1] - props.topLeft[1]) * scale.value + "px");
</script>


<template>
    <div class="bounding-box"
            v-bind:data-topleft="props.topLeft[0] + ',' + props.topLeft[1]"
            v-bind:data-bottomright="props.bottomRight[0] + ',' + props.bottomRight[1]"
            v-bind:data-certainty="props.certainty" v-bind:data-classification="classification"
            v-if="imageState.objectClassifications[classificationIndex].showBoxes">
        <div v-if="viewState.showBoundingBoxInfo">
            <div class="box-certainty">{{ props.certainty }}</div>
            <div class="box-classification">{{ classification }}</div>
        </div>
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
}

.bounding-box .box-certainty {
    background-color: v-bind(boxColor);
    position: absolute;
    line-height: 16px;
    bottom: -16px;
    right: -2px;
    font-size: 12px;
    font-weight: 700;
    color: white;
    padding: 0 3px;
}

.bounding-box .box-classification {
    background-color: v-bind(boxColor);
    position: absolute;
    line-height: 16px;
    bottom: -16px;
    left: -2px;
    font-size: 12px;
    font-weight: 700;
    color: white;
    padding: 0 3px;
}
</style>
