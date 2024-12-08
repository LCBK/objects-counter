<script setup lang="ts">
import { config } from "@/config";
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

const showElementIds = computed({
    get() {
        return settingsState.showElementIds;
    },
    set(value) {
        settingsState.updateElementIdsVisibility(value);
    }
});


onMounted(() => {
    isDarkTheme.value = settingsState.isDarkTheme;
});
</script>


<template>
    <div id="settings-widget">
        <VButton text rounded icon="pi pi-cog" @click="visible = true" />
        <VDialog v-model:visible="visible" modal header="Settings" class="popup"
                id="settings-popup" :dismissable-mask="true">
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
            <div v-if="config.showDebugSettings" class="settings-item">
                <div class="settings-item-label">Show element IDs</div>
                <VInputSwitch class="settings-item-switch" v-model="showElementIds" />
            </div>
            <VButton outlined label="Reset server address" class="reset-server-address"
                    @click="settingsState.resetServerAddress" />
        </VDialog>
    </div>
</template>


<style scoped>
.settings-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    user-select: none;
}

.settings-item:last-child {
    margin-bottom: 0;
}

.settings-heading {
    margin-top: 8px;
    margin-bottom: 12px;
    font-weight: 600;
    user-select: none;
}

.settings-heading:not(:first-child) {
    margin-top: 24px;
}

.settings-item-label {
    font-size: 1rem;
    font-weight: 300;
}

.reset-server-address {
    margin-top: 18px;
    float: left;
}
</style>

<style>
.main-view-nav-bar #settings-widget {
    margin: auto 0 auto 4px;
}

#settings-popup {
    max-width: 400px;
}

@media screen and (min-width: 340px) {
    .main-view-nav-bar #settings-widget {
        margin-left: 8px;
    }
}
</style>
