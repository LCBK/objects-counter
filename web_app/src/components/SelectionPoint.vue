<script setup lang="ts">
import { useImageStateStore } from '@/stores/imageState';
import { computed } from 'vue';


const imageState = useImageStateStore();
const props = defineProps({
    positive: {
        type: Boolean,                  // true - positive, false - negative
        required: true
    },
    position: {
        type: Array<number>,            // [x, y], counted in pixels from top-left corner
        required: true
    }
});

const scale = computed(() => imageState.boundingBoxScale);

// CSS properties
const top = computed(() => (props.position[1]) * scale.value - 12 + "px");
const left = computed(() => (props.position[0]) * scale.value - 12 + "px");
</script>


<template>
    <div class="selection-point"
            :data-positive="props.positive"
            :data-x="props.position[0]" :data-y="props.position[1]">
        {{ props.positive == true ? "+" : "-" }}
    </div>
</template>


<style scoped>
.selection-point {
    position: absolute;
    left: v-bind(left);
    top: v-bind(top);
    width: 24px;
    height: 24px;
    line-height: 20px;
    border-radius: 50%;
    background-color: var(--primary-color);
    color: var(--surface-ground);
    text-align: center;
    font-size: 24px;
    user-select: none;
}

.selection-point.negative {
    background-color: var(--red-400);
}
</style>