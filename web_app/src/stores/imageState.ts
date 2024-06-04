import { defineStore } from "pinia";


export const useImageStateStore = defineStore("imageState", {
    state: () => {
        return {
            isUploading: false,
            isUploaded: false,
            url: ""
        }
    }
});
