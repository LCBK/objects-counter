import { defineStore } from "pinia";


export const useImageStateStore = defineStore("imageState", {
    state: () => {
        return {
            isUploading: false,
            isUploaded: false,
            url: "",
            width: 0,
            height: 0,
            boundingBoxScale: 1,
            result: [{
                top_left: [0, 0], 
                bottom_right: [0, 0], 
                certainty: 0, 
                class: ""
            }]
        }
    }
});
