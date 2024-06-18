<script setup lang="ts">
import { useImageStateStore } from '@/stores/imageState';
import { computed, defineProps } from 'vue';


const imageState = useImageStateStore();
const props = defineProps({
    topLeft: {                          // top-left corner [x, y]
        type: Array<number>,
        required: true
    },
    bottomRight: {                          // bottom-right corner [x, y]
        type: Array<number>,
        required: true
    },
    certainty: {
        type: Number
    },
    class: {
        type: String
    },
});

const boxColor = "red";
const scale = computed(() => imageState.boundingBoxScale);
const top = computed(() => props.topLeft[1] * scale.value + "px");
const left = computed(() => props.topLeft[0] * scale.value + "px");
const width = computed(() => props.bottomRight[0] * scale.value + "px");
const height = computed(() => props.bottomRight[1] * scale.value + "px");
</script>


<template>
    <div class="bounding-box"
            v-if="props.topLeft !== undefined && props.bottomRight !== undefined"
            v-bind:data-topleft="props.topLeft[0] + ',' + props.topLeft[1]"
            v-bind:data-bottomright="props.bottomRight[0] + ',' + props.bottomRight[1]">
        <div class="certainty">{{ props.certainty }}</div>
        <div class="class">{{ props.class }}</div>
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

.bounding-box > * {
    display: none;
}
</style>
