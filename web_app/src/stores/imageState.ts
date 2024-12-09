import type { BackgroundPoint, ImageDetails, ObjectClassification, RenameMapping } from "@/types/app";
import type { ComparisonDiff } from "@/types/requests";
import { distance } from "@/utils";
import { defineStore } from "pinia";


// Stores data related to user's image, e.g.: canvas data/scale/offset, selection points, bounding boxes

const defaultState = {
    images: [] as Array<ImageDetails>,
    classifications: [] as Array<ObjectClassification>,
    classificationRenameMap: [] as Array<RenameMapping>,
    currentImageIndex: 0,
    resultId: 0,
    datasetId: 0,
    scaledImageWidth: 0,
    scaledImageHeight: 0,
    overlayOffsetLeft: 0,
    overlayOffsetTop: 0,
    boundingBoxScale: 1,
    isPanning: false,
    userZoom: 1,
    comparisonDifference: {} as ComparisonDiff,
    comparisonDatasetName: "",
}

export const useImageStateStore = defineStore("imageState", {
    state: () => ({ ...defaultState }),
    getters: {
        currentImage(state) {
            return state.images[state.currentImageIndex];
        },

        allElements(state) {
            return state.images.flatMap(image => image.elements);
        }
    },
    actions: {
        reset() {
            Object.assign(this, defaultState);
            this.images = [];
            this.classifications = [];
            this.classificationRenameMap = [];
            this.comparisonDifference = {};
        },

        addPoint(isPositive: boolean, x: number, y: number) {
            this.currentImage.points.push({ positive: isPositive, position: [x, y] } as BackgroundPoint);
        },

        removeNearbyPoint(x: number, y: number, tolerance: number = 60) {
            if (this.currentImage.points.length === 0) return;

            const closestPoint = this.currentImage.points.reduce((a, b) =>
                distance(a.position[0], a.position[1], x, y) < distance(b.position[0], b.position[1], x, y) ? a : b
            );

            if (distance(closestPoint.position[0], closestPoint.position[1], x, y) < tolerance) {
                const pointIndex = this.currentImage.points.findIndex(p => p == closestPoint);
                this.currentImage.points.splice(pointIndex, 1);
            }
        },

        addClassification(name: string) {
            this.classifications.push({
                name: name,
                showBoxes: true
            });

            this.classificationRenameMap.push({
                originalName: name,
                newName: name
            });
        },

        clearAllResults() {
            this.classifications = [];
            this.classificationRenameMap = [];
            this.comparisonDifference = {};
            this.images.forEach(image => {
                image.elements = [];
            });
        },

        clearCurrentResult() {
            this.currentImage.elements = [];
        },

        clearAllSelections() {
            this.images.forEach(image => {
                image.points = [];
                image.selectedLeaderIds = [];
            });
        },

        clearCurrentSelections() {
            this.currentImage.points = [];
            this.currentImage.selectedLeaderIds = [];
        },
    }
});
