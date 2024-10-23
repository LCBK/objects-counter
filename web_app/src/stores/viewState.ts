import { defineStore } from "pinia";

import MainView from "@/components/views/MainView.vue";
import LoadingView from "@/components/views/LoadingView.vue";
import ImageView from "@/components/views/ImageView.vue";
import UserView from "@/components/views/UserView.vue";
import DebugView from "@/components/views/DebugView.vue";
import DebugCompareView from "@/components/views/DebugCompareView.vue";
import ResultHistoryView from "@/components/views/ResultHistoryView.vue";

import ConfirmPointsToolBar from "@/components/toolbars/ConfirmPointsToolBar.vue";
import EditPointsToolBar from "@/components/toolbars/EditPointsToolBar.vue";
import ResultViewToolBar from "@/components/toolbars/ResultViewToolBar.vue";
import { useImageStateStore } from "./imageState";


// Stores data about current application states and views
// Allows to manage state through setState, handling all state transitions

export enum ViewStates {
    MainView,
    UserView,
    DebugView,
    DebugCompareView,
    Uploading,
    ImageEditPoints,
    ImageConfirmBackground,
    ImageViewResult,
    ResultHistoryView
}

const defaultState = {
    isImageUploading: false,
    isImageUploaded: false,
    isAddingPoint: false,
    isRemovingPoint: false,
    isPointTypePositive: true,
    isWaitingForResponse: false,
    showPoints: true,
    showBackground: false,
    currentNavBarTitle: "",
    currentState: ViewStates.MainView,
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

        setState(state: ViewStates) {
            this.currentState = state;
            this.isWaitingForResponse = false;
            this.isAddingPoint = false;
            this.isRemovingPoint = false;

            switch (state) {
                case ViewStates.MainView:
                    this.reset();
                    break;

                case ViewStates.Uploading:
                    this.currentView = LoadingView;
                    break;

                case ViewStates.ImageEditPoints:
                    this.currentView = ImageView;
                    this.currentImageViewToolBar = EditPointsToolBar;
                    this.currentNavBarTitle = "Select background";
                    this.showPoints = true;
                    this.showBackground = false;
                    break;

                case ViewStates.ImageConfirmBackground:
                    this.currentView = ImageView;
                    this.currentImageViewToolBar = ConfirmPointsToolBar;
                    this.currentNavBarTitle = "Confirm selection";
                    this.showPoints = true;
                    this.showBackground = true;
                    break;

                case ViewStates.ImageViewResult:
                    this.currentView = ImageView;
                    this.currentImageViewToolBar = ResultViewToolBar;
                    this.currentNavBarTitle = "Result";
                    this.showPoints = false;
                    this.showBackground = false;
                    break;

                case ViewStates.UserView:
                    this.currentView = UserView;
                    break;

                case ViewStates.DebugView:
                    this.currentView = DebugView;
                    break;

                case ViewStates.DebugCompareView:
                    this.currentView = DebugCompareView;
                    break;

                case ViewStates.ResultHistoryView:
                    this.currentView = ResultHistoryView;
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
