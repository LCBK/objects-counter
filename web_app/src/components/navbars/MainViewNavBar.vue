<script setup lang="ts">
import VButton from "primevue/button";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { useUserStateStore } from "@/stores/userState";

const viewState = useViewStateStore();
const userState = useUserStateStore();
</script>


<template>
    <div class="main-view-nav-bar nav-bar bar">
        <VButton text rounded icon="pi pi-cog" />
        <VButton text rounded icon="pi pi-user" icon-pos="right" class="user-navbar-button"
                :label=userState.username @click="viewState.setState(ViewStates.UserView)" />
    </div>
</template>


<style>
.user-navbar-button .p-button-label {
    margin-right: 16px;
    font-weight: 500 !important;
}
</style>
