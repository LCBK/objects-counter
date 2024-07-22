import type { Result } from "@/types";
import { defineStore } from "pinia";


const defaultState = {
    url: "",
    width: 0,
    height: 0,
    boundingBoxScale: 1,
    results: [{
        index: 0,
        top_left: [0, 0], 
        bottom_right: [0, 0], 
        certainty: 0, 
        class: "",
        color: "#000000"
    } as Result]
}

export const useImageStateStore = defineStore("imageState", {
    state: () => ({ ...defaultState }),
    actions: {
        reset() {
            Object.assign(this, defaultState);
        }
    }
});
