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
    showPoints: true,
    showBackground: false,
    showBoundingBoxInfo: false,
    currentNavBarTitle: "",
    currentStateName: "beforeUpload",
    currentView: MainView,
    currentImageViewToolBar: EditPointsToolBar
}

export const useViewStateStore = defineStore("viewState", {
    state: () => ({ ...defaultState }),
    actions: {
        reset() {
            Object.assign(this, defaultState);
        },
        
        setState(state: string) {
            this.currentStateName = state;
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
                    this.showPoints = true;
                    this.showBackground = false;
                    break;

                case "confirmBackground":
                    this.currentView = ImageView;
                    this.currentImageViewToolBar = ConfirmPointsToolBar;
                    this.currentNavBarTitle = "Confirm selection";
                    this.isAddingPoint = false;
                    this.isRemovingPoint = false;
                    this.showPoints = true;
                    this.showBackground = true;
                    break;

                case "viewResult":
                    this.currentView = ImageView;
                    this.currentImageViewToolBar = ResultViewToolBar;
                    this.currentNavBarTitle = "Result";
                    this.isAddingPoint = false;
                    this.isRemovingPoint = false;
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
