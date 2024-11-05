import { defineStore } from "pinia";

import MainView from "@/components/views/MainView.vue";
import LoadingView from "@/components/views/LoadingView.vue";
import ImageView from "@/components/views/ImageView.vue";
import UserView from "@/components/views/UserView.vue";
import DebugView from "@/components/views/DebugView.vue";
import DebugCompareView from "@/components/views/DebugCompareView.vue";
import ResultHistoryView from "@/components/views/ResultHistoryView.vue";
import EditPointsToolBar from "@/components/toolbars/EditPointsToolBar.vue";
import ResultViewToolBar from "@/components/toolbars/ResultViewToolBar.vue";
import { useImageStateStore } from "./imageState";
import { shallowRef, type Component } from "vue";


// Stores data about current application states and views
// Allows to manage state through setState, handling all state transitions

export enum ViewStates {
    MainView,
    UserView,
    DebugView,
    DebugCompareView,
    Uploading,
    ImageEditPoints,
    ImageViewResult,
    ResultHistoryView
}

// TODO: refine, rename? what about capture/upload?
export enum ImageAction {
    Simple,
    CreateDataset,
    Compare
}

const defaultState = {
    isImageUploading: false,
    isImageUploaded: false,
    isAddingPoint: false,
    isRemovingPoint: false,
    isPointTypePositive: true,
    isWaitingForResponse: false,
    isEditingExistingResult: false,
    showPoints: true,
    showBackground: false,
    currentNavBarTitle: "",
    currentState: ViewStates.MainView,
    previousState: ViewStates.MainView,
    currentAction: ImageAction.Simple,
    currentView: shallowRef<Component>(MainView),
    currentImageViewToolBar: shallowRef<Component>(EditPointsToolBar)
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
            this.previousState = this.currentState;
            this.currentState = state;
            this.isWaitingForResponse = false;
            this.isAddingPoint = false;
            this.isRemovingPoint = false;

            switch (state) {
                case ViewStates.MainView:
                    this.reset();
                    break;

                case ViewStates.Uploading:
                    this.currentView = shallowRef(LoadingView);
                    break;

                case ViewStates.ImageEditPoints:
                    this.currentView = shallowRef(ImageView);
                    this.currentImageViewToolBar = shallowRef(EditPointsToolBar);
                    this.currentNavBarTitle = "Select background";
                    this.showPoints = true;
                    this.showBackground = false;
                    break;

                case ViewStates.ImageViewResult:
                    this.currentView = shallowRef(ImageView);
                    this.currentImageViewToolBar = shallowRef(ResultViewToolBar);
                    if (this.currentAction === ImageAction.Compare) this.currentNavBarTitle = "Comparison result";
                    else if (this.currentAction === ImageAction.CreateDataset) this.currentNavBarTitle = "Create dataset";
                    else this.currentNavBarTitle = "Result";
                    this.showPoints = false;
                    this.showBackground = false;
                    break;

                case ViewStates.UserView:
                    this.currentView = shallowRef(UserView);
                    this.currentAction = ImageAction.Simple;
                    break;

                case ViewStates.DebugView:
                    this.currentView = shallowRef(DebugView);
                    break;

                case ViewStates.DebugCompareView:
                    this.currentView = shallowRef(DebugCompareView);
                    break;

                case ViewStates.ResultHistoryView:
                    this.currentView = shallowRef(ResultHistoryView);
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
