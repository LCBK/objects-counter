import { defineStore } from "pinia";

import MainView from "../components/views/MainView.vue";
import LoadingView from "../components/views/LoadingView.vue";
import ImageView from "../components/views/ImageView.vue";

import ConfirmPointsToolBar from "../components/ConfirmPointsToolBar.vue";
import EditPointsToolBar from "../components/EditPointsToolBar.vue";
import ResultViewToolBar from "../components/ResultViewToolBar.vue";
import { useImageStateStore } from "./imageState";


// Stores data about current application states and views
// Allows to manage state through setState, handling all state transitions

const defaultState = {
    isImageUploading: false,
    isImageUploaded: false,
    isAddingPoint: false,
    isRemovingPoint: false,
    isPointTypePositive: true,
    isWaitingForResponse: false,
    showPoints: true,
    showBackground: false,
    showBoundingBoxInfo: true,
    currentNavBarTitle: "",
    currentStateName: "beforeUpload",
    currentView: MainView,
    currentImageViewToolBar: EditPointsToolBar
}

export const useViewStateStore = defineStore("viewState", {
    state: () => ({ ...defaultState }),
    actions: {
        reset() {
            const imageState = useImageStateStore();
            imageState.reset();

            Object.assign(this, defaultState);
        },
        
        setState(state: string) {
            this.currentStateName = state;
            this.isWaitingForResponse = false;
            this.isAddingPoint = false;
            this.isRemovingPoint = false;
            
            switch (state) {
                case "beforeUpload":
                    this.reset();
                    this.currentNavBarTitle = "";
                    break;

                case "uploading":
                    this.currentView = LoadingView;
                    this.currentNavBarTitle = "";
                    break;
                
                case "editPoints":
                    this.currentView = ImageView;
                    this.currentImageViewToolBar = EditPointsToolBar;
                    this.currentNavBarTitle = "Select background";
                    this.showPoints = true;
                    this.showBackground = false;
                    break;

                case "confirmBackground":
                    this.currentView = ImageView;
                    this.currentImageViewToolBar = ConfirmPointsToolBar;
                    this.currentNavBarTitle = "Confirm selection";
                    this.showPoints = true;
                    this.showBackground = true;
                    break;

                case "viewResult":
                    this.currentView = ImageView;
                    this.currentImageViewToolBar = ResultViewToolBar;
                    this.currentNavBarTitle = "Result";
                    this.showPoints = false;
                    this.showBackground = false;
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
