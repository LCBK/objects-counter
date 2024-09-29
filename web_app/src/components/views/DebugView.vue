<script setup lang="ts">
import VButton from 'primevue/button'
import { ViewStates, useViewStateStore } from '@/stores/viewState';

const viewState = useViewStateStore();
</script>


<template>
    <div id="debug-view" class="view">
        <VButton icon="pi pi-user" class="wide-button"
                label="User management" @click="viewState.setState(ViewStates.UserView)" />
        <VButton icon="pi pi-home" class="wide-button"
                label="Main view" @click="viewState.setState(ViewStates.MainView)" />
        <VButton icon="pi pi-arrow-right-arrow-left" class="wide-button"
                label="Compare elements" @click="viewState.setState(ViewStates.DebugCompareView)" />
    </div>
</template>


<style scoped>
#debug-view {
    width: 100vw;
    height: 100vh;          /* added for compatibility */
    height: 100dvh;
    display: flex;
    flex-direction: column;
    flex-wrap: nowrap;
    justify-content: center;
    margin: auto 0;
    align-items: center;
    gap: 30px;
}
</style>

<style>
#debug-view .p-button-label {
    font-weight: 600;
}

#debug-view .pi {
    font-size: 1.3rem;
}
</style>
