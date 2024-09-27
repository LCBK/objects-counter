import { defineStore } from "pinia";


// Stores data related to the current user

const defaultState = {
    username: "Guest",
    userId: 0,
    userToken: "",
    isLoggedIn: false
}

export const useUserStateStore = defineStore("userState", {
    state: () => ({ ...defaultState }),
    actions: {
        reset() {
            Object.assign(this, defaultState);
        }
    }
});
