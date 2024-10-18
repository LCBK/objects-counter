<script setup lang="ts">
import VButton from "primevue/button";
import VDialog from "primevue/dialog";
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
const showError = ref<boolean>(false);
const errorText = ref<string>("");

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
            viewState.setState(ViewStates.MainView);
            userState.login(response.data.username, response.data.user_id, response.data.token);
        } else if (response.status === 404) {
            showErrorDialog("Incorrect user or password");
        } else {
            showErrorDialog("Login failed");
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
            viewState.setState(ViewStates.MainView);
            userState.login(response.data.username, response.data.user_id, response.data.token);
        } else if (response.status === 400) {
            showErrorDialog("Invalid data or user already exists");
        } else {
            showErrorDialog("Registration failed");
        }
    });
}

function showErrorDialog(text: string) {
    showError.value = true;
    errorText.value = text;
    setTimeout(() => {
        showError.value = false;
        errorText.value = "";
    }, 2500);
}
</script>


<template>
    <div id="user-view" class="view">
        <Transition name="user-fade" mode="out-in">
            <div v-if="userState.isLoggedIn" class="user-container user-details">
                <p style="color: var(--text-color)">Currently logged in as: <span>{{ userState.username }}</span></p>
                <p style="color: var(--text-color)">TODO: more details</p>
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
                <VDialog v-model:visible="showError" modal :dismissable-mask="false" header="Error" class="user-dialog">
                    <p>{{ errorText }}</p>
                </VDialog>
            </div>
            <div v-else-if="isRegistering" class="user-container user-register">
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
                <VDialog v-model:visible="showError" modal :dismissable-mask="false" header="Error" class="user-dialog">
                    <p>{{ errorText }}</p>
                </VDialog>
            </div>
        </Transition>
        <VButton class="return-button wide-button" icon="pi pi-chevron-left" outlined
                label="Return" @click="onBack()" />
    </div>
</template>


<style scoped>
.user-fade-enter-active, .user-fade-leave-active {
    transition: opacity .2s;
}

.user-fade-enter-from, .user-fade-leave-to {
    opacity: 0;
}

.user-fade-enter-to, .user-fade-leave-from {
    opacity: 1;
}

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
    margin-top: 24px;
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

.user-dialog .p-dialog-header-icons {
    display: none;
}

.user-dialog .p-dialog-header {
    padding: 20px 10px 12px 10px;
}

.user-dialog .p-dialog-header > span {
    width: 100%;
    text-align: center;
}
</style>
