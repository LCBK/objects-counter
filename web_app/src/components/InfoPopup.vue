<script setup lang="ts">
import VDialog from 'primevue/dialog';
import { watch } from 'vue';


const props = defineProps({
    text: String,
    header: String,
    timeout: {
        type: Number,
        default: 3000,
        required: false
    }
});

const visible = defineModel<boolean>();


watch(() => visible.value, (value) => {
    if (props.timeout && value === true) {
        setTimeout(() => {
            visible.value = false;
        }, props.timeout);
    }
});
</script>


<template>
    <VDialog v-model:visible="visible" modal :dismissable-mask="true" :header="header" class="popup">
        <p>{{ text }}</p>
    </VDialog>
</template>


<style>
.popup .p-dialog-header-icons {
    display: none;
}

.popup .p-dialog-header {
    padding: 20px 10px;
}

.popup .p-dialog-content {
    text-align: center;
}

.popup .p-dialog-header > span {
    width: 100%;
    text-align: center;
}
</style>
