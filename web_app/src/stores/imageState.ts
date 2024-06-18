import { defineStore } from "pinia";


export const useImageStateStore = defineStore("imageState", {
    state: () => {
        return {
            isUploading: false,
            isUploaded: false,
            url: "",
            result: [{
                top_left: [0, 0], 
                bottom_right: [0, 0], 
                certainty: 0, 
                class: ""
            }]
        }
    }
});
