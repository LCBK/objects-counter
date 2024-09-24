<script setup lang="ts">
import VButton from "primevue/button";
import VInputGroup from "primevue/inputgroup";
import VInputGroupAddon from "primevue/inputgroupaddon";
import VInputText from "primevue/inputtext";
import VPassword from "primevue/password";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { useUserStateStore } from "@/stores/userState";
import { ref } from "vue";

const viewState = useViewStateStore();
const userState = useUserStateStore();

const username = defineModel<string>("username");
const password = defineModel<string>("password");
const confirmPassword = defineModel<string>("confirm");

const isRegistering = ref<boolean>(false);

function onBack() {
    viewState.setState(ViewStates.MainView);
}
</script>


<template>
    <div id="user-view" class="view">
        <div v-if="userState.isLoggedIn" class="user-container user-details">
            
        </div>
        <div v-else-if="!isRegistering" class="user-container user-login">
            <p class="login-label">Login</p>
            <p class="login-label-small">Sign in to access history and comparison.</p>
            <VInputGroup class="user-input">
                <VInputGroupAddon>
                    <i class="pi pi-user"></i>
                </VInputGroupAddon>
                <VInputText v-model:username="username" placeholder="Username" />
            </VInputGroup>
            <VInputGroup class="user-input">
                <VInputGroupAddon>
                    <i class="pi pi-key"></i>
                </VInputGroupAddon>
                <VPassword v-model:password="password" placeholder="Password" :feedback="false" toggle-mask />
            </VInputGroup>
            <VButton class="login-button wide-button" icon="pi pi-sign-in" icon-pos="right"
                    label="Login" @click="onBack()" />
            <p class="register-notice">Don't have an account?
                <VButton class="register-button" text label="Register" @click="isRegistering = true" />
            </p>
        </div>
        <div v-else class="user-container user-register">
            <p class="login-label">Register</p>
            <p class="login-label-small-first">Create a new account.</p>
            <p class="login-label-small">TBD data collection statement/details.</p>
            <VInputGroup class="user-input">
                <VInputGroupAddon>
                    <i class="pi pi-user"></i>
                </VInputGroupAddon>
                <VInputText v-model:username="username" placeholder="Username" />
            </VInputGroup>
            <VInputGroup class="user-input">
                <VInputGroupAddon>
                    <i class="pi pi-key"></i>
                </VInputGroupAddon>
                <VPassword v-model:password="password" placeholder="Password"
                        :feedback="false" toggle-mask />
            </VInputGroup>
            <VInputGroup class="user-input">
                <VInputGroupAddon>
                    <i class="pi pi-key"></i>
                </VInputGroupAddon>
                <VPassword v-model:confirm="confirmPassword" placeholder="Confirm password"
                        :feedback="false" toggle-mask />
            </VInputGroup>
            
            <VButton class="login-button wide-button" icon="pi pi-sign-in" icon-pos="right"
                    label="Login" @click="onBack()" />
            <p class="register-notice">Want to login instead?
                <VButton class="register-button" text label="Login" @click="isRegistering = false" />
            </p>
        </div>
        <VButton class="return-button wide-button" icon="pi pi-chevron-left" outlined
                label="Return" @click="onBack()" />
    </div>
</template>


<style scoped>
#user-view {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 30px;
    padding: 20px;
}

#user-view .user-container {
    display: flex;
    flex-direction: column;
    align-items: center;
}

#user-view .login-label {
    text-align: center;
    color: var(--vt-c-text-dark-1);
    font-size: 1.45rem;
    font-weight: 700;
    letter-spacing: 0.4px;
    margin-bottom: 10px;
}

#user-view .login-label-small {
    text-align: center;
    color: var(--vt-c-text-dark-2);
    font-size: 0.85rem;
    font-weight: 400;
    letter-spacing: 0.3px;
    margin-bottom: 40px;
}

#user-view .login-label-small-first {
    margin-bottom: 0px;
}

#user-view .user-input {
    margin-bottom: 15px;
}

#user-view .login-button {
    height: 38px;
    width: 100%;
    max-width: 100%;
    margin-top: 14px;
}

#user-view .register-notice {
    text-align: center;
    color: var(--vt-c-text-dark-2);
    font-size: 0.85rem;
    font-weight: 400;
    letter-spacing: 0.3px;
    margin-top: 40px;
}

#user-view .register-button {
    padding: 0;
    display: inline;
    vertical-align: baseline;
}

#user-view .return-button {
    position: absolute;
    bottom: 40px;
}
</style>

<style>
#user-view .register-button .p-button-label {
    font-size: 0.85rem;
}
</style>
