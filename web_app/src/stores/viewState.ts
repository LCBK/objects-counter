import { defineStore } from "pinia";

import MainView from "../components/views/MainView.vue";
import LoadingView from "../components/views/LoadingView.vue";
import ImageView from "../components/views/ImageView.vue";

import ConfirmPointsToolBar from "../components/ConfirmPointsToolBar.vue";
import EditPointsToolBar from "../components/EditPointsToolBar.vue";
import ResultViewToolBar from "../components/ResultViewToolBar.vue";


const defaultState = {
    isImageUploading: false,
    isImageUploaded: false,
    hasReceivedResult: false,
    isAddingPoint: false,
    isRemovingPoint: false,
    currentNavBarTitle: "",
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
                    this.currentNavBarTitle = "";
                    this.isAddingPoint = false;
                    this.isRemovingPoint = false;
                    break;

                case "uploading":
                    this.currentView = LoadingView;
                    this.currentNavBarTitle = "";
                    this.isAddingPoint = false;
                    this.isRemovingPoint = false;
                    break;
                
                case "editPoints":
                    this.currentView = ImageView;
                    this.currentImageViewToolBar = EditPointsToolBar;
                    this.currentNavBarTitle = "Select background";
                    this.isAddingPoint = false;
                    this.isRemovingPoint = false;
                    break;

                case "confirmBackground":
                    this.currentView = ImageView;
                    this.currentImageViewToolBar = ConfirmPointsToolBar;
                    this.currentNavBarTitle = "Confirm selection";
                    this.isAddingPoint = false;
                    this.isRemovingPoint = false;
                    break;

                case "viewResult":
                    this.currentView = ImageView;
                    this.currentImageViewToolBar = ResultViewToolBar;
                    this.currentNavBarTitle = "Result";
                    this.isAddingPoint = false;
                    this.isRemovingPoint = false;
                    break;
            }
        },

        toggleAddPoint() {
            this.isAddingPoint = !this.isAddingPoint;
            if (this.isAddingPoint) this.isRemovingPoint = false;
        },

        toggleRemovePoint() {
            this.isRemovingPoint = !this.isRemovingPoint;
            if (this.isRemovingPoint) this.isAddingPoint = false;
        }
    }
});
