<script setup lang="ts">
import VButton from "primevue/button";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { useUserStateStore } from "@/stores/userState";
import SettingsWidget from "../SettingsWidget.vue";

const viewState = useViewStateStore();
const userState = useUserStateStore();
</script>


<template>
    <div class="main-view-nav-bar nav-bar bar">
        <div class="nav-bar-content bar-content">
            <SettingsWidget />
            <VButton text rounded icon="pi pi-user" icon-pos="right" class="user-navbar-button"
                    :label=userState.username @click="viewState.setState(ViewStates.UserView)" />
        </div>
    </div>
</template>


<style>
.user-navbar-button .p-button-label {
    margin-right: 16px;
    font-weight: 500 !important;
}

@media (min-width: 340px) {
    .user-navbar-button .p-button-label {
        font-size: 1.2rem;
    }
}
</style>
