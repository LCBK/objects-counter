<script setup lang="ts">
import VButton from "primevue/button";
import VInputGroup from "primevue/inputgroup";
import VInputGroupAddon from "primevue/inputgroupaddon";
import VInputText from "primevue/inputtext";
import VPassword from "primevue/password";
import { useViewStateStore, ViewStates } from "@/stores/viewState";
import { useUserStateStore } from "@/stores/userState";
import { computed, ref } from "vue";
import { config, endpoints } from "@/config";
import { type Response, sendRequest } from "@/utils";

const viewState = useViewStateStore();
const userState = useUserStateStore();

const username = ref<string>("");
const password = ref<string>("");
const confirmPassword = ref<string>("");
const isRegistering = ref<boolean>(false);
const loginForm = ref<HTMLFormElement>();
const registerForm = ref<HTMLFormElement>();

const isLoginValid = computed(() => {
    return (
        validateUsername(username.value) &&
        validatePassword(password.value)
    );
});

const isRegisterValid = computed(() => {
    return (
        validateUsername(username.value) &&
        validatePassword(password.value) &&
        password.value == confirmPassword.value
    );
})

function validateUsername(username: string) {
    if (username === undefined) return false;
    if (username.length < config.minUsernameLength) return false;
    if (username.length > config.maxUsernameLength) return false;
    return true;
}

function validatePassword(password: string) {
    if (password === undefined) return false;
    if (password.length < config.minPasswordLength) return false;
    if (password.length > config.maxPasswordLength) return false;
    if (config.requirePasswordDigit && password.search(/\d/) == -1) return false;
    if (config.requirePasswordSymbol && password.search(/[!@#_%&$^*()+]/) == -1) return false;
    if (config.requirePasswordLowerChar && password.search(/[a-z]/) == -1) return false;
    if (config.requirePasswordUpperChar && password.search(/[A-Z]/) == -1) return false;
    return true;
}

function onBack() {
    username.value = "";
    password.value = "";
    confirmPassword.value = "";
    isRegistering.value = false;
    viewState.setState(ViewStates.MainView);
}

function onLogout() {
    userState.logout();
}

function submitLoginForm() {
    loginForm.value!.submit();      // For triggering credential saving in browsers (action set to "javascript:void(0);")

    const requestUri = config.serverUri + endpoints.userLogin;
    const requestData = JSON.stringify({
        "username": username.value,
        "password": password.value
    });
    const responsePromise = sendRequest(requestUri, requestData, "POST");

    responsePromise.then((response: Response) => {
        if (response.status === 200) {
            alert(`TODO: proper response handling\nSUCCESS: id ${response.data.user_id}, token ${response.data.token}, ${response.data.username}`);
            userState.login(response.data.username, response.data.user_id, response.data.token);
        } else {
            alert(`TODO: proper response handling\nFAILED: ${response.data}`);
        }
    });
}

function submitRegisterForm() {
    registerForm.value!.submit();   // For triggering credential saving in browsers

    const requestUri = config.serverUri + endpoints.userRegister;
    const requestData = JSON.stringify({
        "username": username.value,
        "password": password.value
    });
    const responsePromise = sendRequest(requestUri, requestData, "POST");

    responsePromise.then((response: Response) => {
        if (response.status === 201) {
            alert(`TODO: proper response handling\nSUCCESS: id ${response.data.user_id}, ${response.data.username}`);
        } else {
            alert(`TODO: proper response handling\nFAILED: ${response.data}`);
        }
    });
}

// todo: proper response handling
</script>


<template>
    <div id="user-view" class="view">
        <div v-if="userState.isLoggedIn" class="user-container user-details">
            <p style="color: var(--vt-c-text-dark-1)">Currently logged in as: <span>{{ userState.username }}</span></p>
            <p style="color: var(--vt-c-text-dark-1)">TODO: more details</p>
            <VButton class="logout-button wide-button" icon="pi pi-sign-out" label="Logout" @click="onLogout()" />
        </div>
        <div v-else-if="!isRegistering" class="user-container user-login">
            <p class="login-label">Login</p>
            <p class="login-label-small">Sign in to access history and comparison.</p>
            <form name="login" ref="loginForm" action="javascript:void(0);">
                <VInputGroup class="user-input">
                    <VInputGroupAddon>
                        <i class="pi pi-user"></i>
                    </VInputGroupAddon>
                    <VInputText v-model="username" placeholder="Username" />
                </VInputGroup>
                <VInputGroup class="user-input">
                    <VInputGroupAddon>
                        <i class="pi pi-key"></i>
                    </VInputGroupAddon>
                    <VPassword v-model="password" placeholder="Password" :feedback="false" toggle-mask />
                </VInputGroup>
                <VButton class="login-button wide-button" icon="pi pi-sign-in" icon-pos="right"
                        label="Login" @click="submitLoginForm()" :disabled="!isLoginValid" />
            </form>
            <p class="register-notice">Don't have an account?
                <VButton class="register-button" text label="Register" @click="isRegistering = true" />
            </p>
        </div>
        <div v-else class="user-container user-register">
            <p class="login-label">Register</p>
            <p class="login-label-small-first">Create a new account.</p>
            <p class="login-label-small">TBD data collection statement/details.</p>
            <form name="register" ref="registerForm" action="javascript:void(0);">
                <VInputGroup class="user-input">
                    <VInputGroupAddon>
                        <i class="pi pi-user"></i>
                    </VInputGroupAddon>
                    <VInputText v-model="username" placeholder="Username" />
                </VInputGroup>
                <VInputGroup class="user-input">
                    <VInputGroupAddon>
                        <i class="pi pi-key"></i>
                    </VInputGroupAddon>
                    <VPassword v-model="password" placeholder="Password"
                            :feedback="false" toggle-mask />
                </VInputGroup>
                <VInputGroup class="user-input">
                    <VInputGroupAddon>
                        <i class="pi pi-key"></i>
                    </VInputGroupAddon>
                    <VPassword v-model="confirmPassword" placeholder="Confirm password"
                            :feedback="false" toggle-mask />
                </VInputGroup>
                <VButton class="login-button wide-button" icon="pi pi-sign-in" icon-pos="right"
                        label="Register" @click="submitRegisterForm()" :disabled="!isRegisterValid" />
            </form>
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
    width: 100%;
}

#user-view .login-label {
    text-align: center;
    color: var(--text-color);
    font-size: 1.45rem;
    font-weight: 700;
    letter-spacing: 0.4px;
    margin-bottom: 10px;
}

#user-view .login-label-small,
#user-view .login-label-small-first {
    text-align: center;
    color: var(--text-color-secondary);
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
    margin-top: 12px;
}

#user-view .logout-button {
    margin-top: 20px;
}

#user-view .register-notice {
    text-align: center;
    color: var(--text-color-secondary);
    font-size: 0.85rem;
    font-weight: 400;
    letter-spacing: 0.3px;
    margin-top: 30px;
    user-select: none;
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
