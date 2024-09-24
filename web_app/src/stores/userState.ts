import { defineStore } from "pinia";


// Stores data related to the current user

const defaultState = {
    username: "Guest",
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
