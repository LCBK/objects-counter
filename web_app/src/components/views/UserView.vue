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
import InfoPopup from "../InfoPopup.vue";


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
            errorText.value = "Incorrect user or password";
            showError.value = true;
        } else {
            errorText.value = "Login failed";
            showError.value = true;
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

            const loginRequestUri = config.serverUri + endpoints.userLogin;
            const loginRequestData = JSON.stringify({
                "username": username.value,
                "password": password.value
            });

            const loginResponsePromise = sendRequest(loginRequestUri, loginRequestData, "POST");
            loginResponsePromise.then((response: Response) => {
                if (response.status === 200) {
                    userState.login(response.data.username, response.data.user_id, response.data.token);
                }
            });
        } else if (response.status === 400) {
            errorText.value = "Invalid data or user already exists";
            showError.value = true;
        } else {
            errorText.value = "Registration failed";
            showError.value = true;
        }
    });
}
</script>


<template>
    <div id="user-view" class="view">
        <Transition name="fade" mode="out-in">
            <div v-if="userState.isLoggedIn" class="user-container user-details">
                <div class="user-details-header">
                    <i class="pi pi-user"></i>
                    <p class="user-details-name">{{ userState.username }}</p>
                </div>
                <div class="user-details-actions">
                    <VButton class="results-button wide-button" icon="pi pi-calendar" label="Counting history" @click="viewState.setState(ViewStates.BrowseResultHistory)" />
                    <VButton class="results-button wide-button" icon="pi pi-calendar" label="Comparison history" />
                    <VButton class="datasets-button wide-button" icon="pi pi-images" label="Datasets" @click="viewState.setState(ViewStates.BrowseDatasets)" />
                </div>
                <VButton outlined class="logout-button wide-button" icon="pi pi-sign-out" label="Logout" @click="onLogout()" />
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
                <p class="register-notice">
                    Don't have an account?
                    <VButton class="register-button" text label="Register" @click="isRegistering = true" />
                </p>
            </div>
            <div v-else-if="isRegistering" class="user-container user-register">
                <p class="login-label">Register</p>
                <p class="login-label-small">Create a new account.</p>
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
        </Transition>
        <InfoPopup v-model="showError" header="Error" :text="errorText" :timeout="2500" />
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
}

#user-view .user-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    position: relative;
    bottom: 40px;
}

#user-view .login-label {
    text-align: center;
    color: var(--text-color);
    font-size: 1.45rem;
    font-weight: 700;
    letter-spacing: 0.4px;
    margin-bottom: 10px;
}

#user-view .login-label-small {
    text-align: center;
    color: var(--text-color-secondary);
    font-size: 0.85rem;
    font-weight: 400;
    letter-spacing: 0.3px;
    margin-bottom: 40px;
}

#user-view .user-input {
    margin-bottom: 15px;
}

#user-view .login-button {
    height: 38px;
    width: 100%;
    max-width: 100%;
    margin-top: 16px;
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

#user-view .user-details .logout-button {
    margin-top: 60px;
}

#user-view .user-details {
    height: 100%;
    justify-content: flex-start;
    margin-bottom: 120px;
    margin-top: 20px;
}

#user-view .user-details-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    color: var(--primary-color);
    width: 100%;
    padding: 60px 40px 40px 40px;
}

#user-view .user-details-header i {
    font-size: 3.5rem;
    margin: 0 0 20px 0;
}

#user-view .user-details-name {
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: 0.4px;
}

#user-view .user-details-actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 30px;
    margin-top: 20px;
    width: 100%;
}

@media screen and (min-width: 340px) {
    #user-view .login-button {
        height: 44px;
    }
}

@media screen and (min-width: 400px) {
    #user-view .login-label {
        font-size: 1.6rem;
    }

    #user-view .login-label-small {
        font-size: 0.95rem;
    }

    #user-view .login-button {
        height: 42px;
    }

    #user-view .register-notice {
        font-size: 0.9rem;
    }

    #user-view .user-details-header i {
        font-size: 4rem;
    }

    #user-view .user-details-name {
        font-size: 1.5rem;
    }
}
</style>

<style>
#user-view .register-button .p-button-label {
    font-size: 0.85rem;
}

#user-view .login-button .pi,
#user-view .register-button .pi {
    font-size: 1.1rem;
}
</style>
