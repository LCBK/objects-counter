<script setup lang="ts">
import VButton from 'primevue/button'
import VInputText from "primevue/inputtext";
import { ViewStates, useViewStateStore } from '@/stores/viewState';
import { onMounted, ref } from 'vue';
import { useUserStateStore } from '@/stores/userState';
import { config, endpoints } from '@/config';
import { type Response, sendRequest } from '@/utils';

const userState = useUserStateStore();
const viewState = useViewStateStore();

const firstImageId = ref<string>();
const secondImageId = ref<string>();
const userResults = ref<string>();
const comparisonResult = ref<string>();

function onCompare() {
    const requestUri = config.serverUri + endpoints.compareElements;
    const requestData = JSON.stringify({
        "first_image_id": firstImageId.value,
        "second_image_id": secondImageId.value
    });
    const responsePromise = sendRequest(requestUri, requestData, "POST");

    responsePromise.then((response: Response) => {
        comparisonResult.value = response.data;
    });
}

onMounted(() => {
    const requestUri = config.serverUri + endpoints.results;
    const responsePromise = sendRequest(requestUri, null, "GET");

    responsePromise.then((response: Response) => {
        userResults.value = response.data;
    });
});
</script>


<template>
    <div id="debug-compare-view">
        <p>Results for user <b>{{ userState.username }}</b> (login required):</p>
        <pre class="resultpre">{{ userResults }}</pre>
        <p>CTRL+A and copy to an editor for legibility</p>
        <p style="margin-top: 15px;">First image ID ("image_id" field)</p>
        <VInputText v-model="firstImageId" />
        <p>Second image ID ("image_id" field)</p>
        <VInputText v-model="secondImageId" />
        <p style="margin-top: 15px;">Comparison result:</p>
        <pre class="comparepre">{{ comparisonResult }}</pre>
        <VButton class="compare-button wide-button" label="Compare results" 
                @click="onCompare()" />
        <VButton class="return-button wide-button" icon="pi pi-chevron-left" outlined
                label="Return" @click="viewState.setState(ViewStates.DebugView)" />
    </div>
</template>


<style scoped>
#debug-compare-view {
    width: 100vw;
    height: 100vh;          /* added for compatibility */
    height: 100dvh;
    display: flex;
    flex-direction: column;
    flex-wrap: nowrap;
    justify-content: center;
    margin: auto 0;
    align-items: center;
    gap: 10px;
    color: var(--text-color);
    user-select: none;
}

#debug-compare-view .compare-button {
    margin-top: 30px;
}

#debug-compare-view .return-button {
    margin-top: 10px;
}

#debug-compare-view .resultpre {
    font-size: 0.6rem;
    height: 250px;
    overflow: scroll;
    user-select: text;
}

#debug-compare-view .comparepre {
    font-size: 0.8rem;
    user-select: text;
}
</style>
