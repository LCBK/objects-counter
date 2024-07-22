import { defineStore } from "pinia";
import { shallowRef } from "vue";

import MainView from "../components/MainView.vue";
import LoadingView from "../components/LoadingView.vue";
import ImageView from "../components/ImageView.vue";

import ConfirmPointsToolBar from "../components/ConfirmPointsToolBar.vue";
import EditPointsToolBar from "../components/EditPointsToolBar.vue";
import ResultViewToolBar from "../components/ResultViewToolBar.vue";


const defaultState = {
    isImageUploading: false,
    isImageUploaded: false,
    hasReceivedResult: false,
    currentView: MainView,
    currentImageViewToolBar: EditPointsToolBar
}

export const useViewStateStore = defineStore("viewState", {
    state: () => ({ ...defaultState }),
    actions: {
        reset() {
            Object.assign(this, defaultState);
        },
        
        // Available states: beforeUpload, uploading, editPoints, confirmBackground, viewResult
        setState(state: string) {
            switch (state) {
                case "beforeUpload":
                    this.reset();
                    break;

                case "uploading":
                    this.currentView = LoadingView;
                    break;
                
                case "editPoints":
                    this.currentView = ImageView;
                    this.currentImageViewToolBar = EditPointsToolBar;
                    break;

                case "confirmBackground":
                    this.currentView = ImageView;
                    this.currentImageViewToolBar = ConfirmPointsToolBar;
                    break;

                case "viewResult":
                    this.currentView = ImageView;
                    this.currentImageViewToolBar = ResultViewToolBar;
                    break;
            }
        }
    }
});
