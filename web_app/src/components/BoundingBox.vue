<script setup lang="ts">
import { defineProps } from 'vue';

const props = defineProps({
    topLeft: Array<Number>,             // top-left corner [x, y]
    bottomRight: Array<Number>,         // bottom-right corner [x, y]
    certainty: Number,
    class: String
});

const boxColor = "red";
let top: String = "0px", left: String = "0px";
let width: String = "0px", height: String = "0px";

if (props.topLeft != undefined) {
    left = props.topLeft[0] + "px";
    top = props.topLeft[1] + "px";
}

if (props.bottomRight != undefined) {
    width = props.bottomRight[0] + "px";
    height = props.bottomRight[1] + "px";
}
</script>


<template>
    <div class="bounding-box">
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
