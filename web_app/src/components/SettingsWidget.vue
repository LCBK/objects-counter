<script setup lang="ts">
import { useSettingsStateStore } from "@/stores/settingsState";
import VButton from "primevue/button";
import VDialog from "primevue/dialog";
import VInputSwitch from "primevue/inputswitch";
import { computed, onMounted } from "vue";


const settingsState = useSettingsStateStore();

const visible = defineModel<boolean>("visible");
const isDarkTheme = computed({
    get() {
        return settingsState.isDarkTheme;
    },
    set(value) {
        if (value === true) settingsState.setDarkTheme();
        else settingsState.setLightTheme();
    }
});

const showBoxLabel = computed({
    get() {
        return settingsState.showBoxLabel;
    },
    set(value) {
        settingsState.updateBoxLabelVisibility(value);
    }
});

const showBoxCertainty = computed({
    get() {
        return settingsState.showBoxCertainty;
    },
    set(value) {
        settingsState.updateBoxCertaintyVisibility(value);
    }
});


onMounted(() => {
    isDarkTheme.value = settingsState.isDarkTheme;
});
</script>


<template>
    <div id="settings-widget">
        <VButton text rounded icon="pi pi-cog" @click="visible = true" />
        <VDialog v-model:visible="visible" modal header="Settings" class="popup" id="settings-popup" :dismissable-mask="true">
            <h3 class="settings-heading">Appearance</h3>
            <div class="settings-item">
                <div class="settings-item-label">Use dark theme</div>
                <VInputSwitch class="settings-item-switch" v-model="isDarkTheme" />
            </div>
            <h3 class="settings-heading">Bounding boxes</h3>
            <div class="settings-item">
                <div class="settings-item-label">Show labels</div>
                <VInputSwitch class="settings-item-switch" v-model="showBoxLabel" />
            </div>
            <div class="settings-item">
                <div class="settings-item-label">Show certainties</div>
                <VInputSwitch class="settings-item-switch" v-model="showBoxCertainty" />
            </div>
        </VDialog>
    </div>
</template>


<style scoped>
.settings-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.settings-item:last-child {
    margin-bottom: 0;
}

.settings-heading {
    margin-top: 8px;
    margin-bottom: 12px;
    font-weight: 600;
}

.settings-heading:not(:first-child) {
    margin-top: 24px;
}

.settings-item-label {
    font-size: 1rem;
    font-weight: 300;
}
</style>
