import { defineStore } from "pinia";

import MainView from "@/components/views/MainView.vue";
import LoadingView from "@/components/views/LoadingView.vue";
import ImageView from "@/components/views/ImageView.vue";
import UserView from "@/components/views/UserView.vue";
import ResultHistoryView from "@/components/views/ResultHistoryView.vue";
import EditPointsToolBar from "@/components/toolbars/EditPointsToolBar.vue";
import BrowseDatasetsView from "@/components/views/BrowseDatasetsView.vue";
import { useImageStateStore } from "./imageState";
import { shallowRef, type Component } from "vue";
import CountingResultToolBar from "@/components/toolbars/CountingResultToolBar.vue";
import ConfirmCountingToolBar from "@/components/toolbars/ConfirmCountingToolBar.vue";
import SelectLeadersToolBar from "@/components/toolbars/SelectLeadersToolBar.vue";
import ConfirmDatasetToolBar from "@/components/toolbars/ConfirmDatasetToolBar.vue";
import ComparisonSelectToolBar from "@/components/toolbars/ComparisonSelectToolBar.vue";
import ComparisonResultToolBar from "@/components/toolbars/ComparisonResultToolBar.vue";
import ComparisonHistoryView from "@/components/views/ComparisonHistoryView.vue";


// Stores data about current application states and views
// Allows to manage state through setState, handling all state transitions

// All possible views of the application
export enum ViewStates {
    MainView,
    UserView,
    Uploading,
    ImageViewEditPoints,
    ImageViewSelectLeaders,
    ImageViewConfirmCounting,
    ImageViewCountingResult,
    ImageViewConfirmDataset,
    ImageViewCompareWithDataset,
    ImageViewComparisonResult,
    BrowseResultHistory,
    BrowseComparisonHistory,
    BrowseDatasets
}

// Actions selected by the user in the main view, these determine how certain components behave
export enum ImageAction {
    AutomaticCounting,
    LeaderCounting,
    CreateDataset,
    CompareWithDataset,
    PreviewDataset
}

const defaultState = {
    isAddingPoint: false,
    isRemovingPoint: false,
    isPointTypePositive: true,
    isWaitingForResponse: false,
    isSelectingAssignment: false,
    isAssigningClassifications: false,
    isAddingMoreImages: false,
    currentlyAssignedClassificationName: "",
    lastAssignedLeaderNumber: 0,
    showPoints: true,
    showBackground: false,
    currentNavBarTitle: "",
    currentState: ViewStates.MainView,
    previousState: ViewStates.MainView,
    currentAction: ImageAction.AutomaticCounting,
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

                case ViewStates.ImageViewEditPoints:
                    this.currentView = shallowRef(ImageView);
                    this.currentImageViewToolBar = shallowRef(EditPointsToolBar);
                    this.currentNavBarTitle = "Select background";
                    this.showPoints = true;
                    this.showBackground = true;
                    break;

                case ViewStates.ImageViewConfirmCounting:
                    this.currentView = shallowRef(ImageView);
                    this.currentImageViewToolBar = shallowRef(ConfirmCountingToolBar);
                    this.currentNavBarTitle = "Confirm selection";
                    this.showPoints = false;
                    this.showBackground = false;
                    break;

                case ViewStates.ImageViewCountingResult:
                    this.currentView = shallowRef(ImageView);
                    this.currentImageViewToolBar = shallowRef(CountingResultToolBar);
                    this.currentNavBarTitle = "Counted elements";
                    this.showPoints = false;
                    this.showBackground = false;
                    break;

                case ViewStates.ImageViewComparisonResult:
                    this.currentView = shallowRef(ImageView);
                    this.currentImageViewToolBar = shallowRef(ComparisonResultToolBar);
                    this.currentNavBarTitle = "Comparison";
                    this.showPoints = false;
                    this.showBackground = false;
                    break;

                case ViewStates.ImageViewSelectLeaders:
                    this.currentView = shallowRef(ImageView);
                    this.currentImageViewToolBar = shallowRef(SelectLeadersToolBar);
                    this.currentNavBarTitle = "Select leaders";
                    this.showPoints = false;
                    this.showBackground = false;
                    this.isAssigningClassifications = false;
                    this.isSelectingAssignment = false;
                    break;

                case ViewStates.ImageViewConfirmDataset:
                    this.currentView = shallowRef(ImageView);
                    this.currentImageViewToolBar = shallowRef(ConfirmDatasetToolBar);
                    this.currentNavBarTitle = "Confirm dataset";
                    this.showPoints = false;
                    this.showBackground = false;
                    this.isAssigningClassifications = false;
                    this.isSelectingAssignment = false;
                    break;

                case ViewStates.ImageViewCompareWithDataset:
                    this.currentView = shallowRef(ImageView);
                    this.currentImageViewToolBar = shallowRef(ComparisonSelectToolBar);
                    this.currentNavBarTitle = "Comparison";
                    this.showPoints = false;
                    this.showBackground = false;
                    break;

                case ViewStates.UserView:
                    this.currentView = shallowRef(UserView);
                    this.currentAction = ImageAction.AutomaticCounting;
                    break;

                case ViewStates.BrowseResultHistory:
                    this.currentView = shallowRef(ResultHistoryView);
                    break;

                case ViewStates.BrowseComparisonHistory:
                    this.currentView = shallowRef(ComparisonHistoryView);
                    break;

                case ViewStates.BrowseDatasets:
                    this.currentView = shallowRef(BrowseDatasetsView);
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
