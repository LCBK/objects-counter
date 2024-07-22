<script setup lang="ts">
import { useImageStateStore } from '@/stores/imageState';
import { computed } from 'vue';

const imageState = useImageStateStore();
const props = defineProps({
    isPositive: {
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
            :data-positive="props.isPositive"
            :data-x="props.position[0]" :data-y="props.position[1]">
        {{ props.isPositive == true ? "+" : "-" }}
    </div>
</template>


<style scoped>
.selection-point {
    position: absolute;
    left: v-bind(left);
    top: v-bind(top);
    width: 24px;
    height: 24px;
    line-height: 18px;
    padding-right: 1px;
    border-radius: 50%;
    background-color: #60a5fa;
    color: #121212;
    text-align: center;
    font-size: 1.5rem;
    user-select: none;
}
</style>