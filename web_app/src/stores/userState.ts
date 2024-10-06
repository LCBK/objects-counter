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
        },

        login(username: string, userId: number, userToken: string) {
            this.username = username;
            this.userId = userId;
            this.userToken = userToken;
            this.isLoggedIn = true;

            document.cookie = `username=${username}; path=/; sameSite=strict; expires=Fri, 31 Dec 9999 23:59:59 GMT`;
            document.cookie = `userId=${userId}; path=/; sameSite=strict; expires=Fri, 31 Dec 9999 23:59:59 GMT`;
            document.cookie = `userToken=${userToken}; path=/; sameSite=strict; expires=Fri, 31 Dec 9999 23:59:59 GMT`;
        },

        logout() {
            this.reset();

            document.cookie = "username=; path=/; sameSite=strict; expires=Thu, 01 Jan 1970 00:00:00 GMT";
            document.cookie = "userId=; path=/; sameSite=strict; expires=Thu, 01 Jan 1970 00:00:00 GMT";
            document.cookie = "userToken=; path=/; sameSite=strict; expires=Thu, 01 Jan 1970 00:00:00 GMT";
        },

        loadFromCookies() {
            const cookies = document.cookie.split("; ");
            for (const cookie of cookies) {
                const [name, value] = cookie.split("=");
                switch (name) {
                    case "username":
                        if (value === "") break;
                        this.username = value;
                        break;
                    case "userId":
                        if (value === "") break;
                        this.userId = parseInt(value);
                        break;
                    case "userToken":
                        if (value === "") break;
                        this.userToken = value;
                        break;
                }
            }

            this.isLoggedIn = this.userToken !== "";
        }
    }
});
