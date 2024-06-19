<script setup lang="ts">
import { useImageStateStore } from '@/stores/imageState';
import { computed, defineProps } from 'vue';


const imageState = useImageStateStore();
const props = defineProps({
    index: {
        type: Number,
        required: true
    },
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
    color: {
        type: String
    }
});

const boxColor = computed(() => props.color);
const scale = computed(() => imageState.boundingBoxScale);
const top = computed(() => props.topLeft[1] * scale.value + "px");
const left = computed(() => props.topLeft[0] * scale.value + "px");
const width = computed(() => props.bottomRight[0] * scale.value + "px");
const height = computed(() => props.bottomRight[1] * scale.value + "px");
</script>


<template>
    <div class="bounding-box"
            v-bind:data-topleft="props.topLeft[0] + ',' + props.topLeft[1]"
            v-bind:data-bottomright="props.bottomRight[0] + ',' + props.bottomRight[1]"
            v-bind:data-certainty="props.certainty" v-bind:data-class="props.class"
            v-bind:data-index="props.index">
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
</style>
