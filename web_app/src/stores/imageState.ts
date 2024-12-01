import type { BackgroundPoint, ImageDetails } from "@/types/app";
import type { ComparisonDiff } from "@/types/requests";
import { distance } from "@/utils";
import { defineStore } from "pinia";


// Stores data related to user's image, e.g.: canvas data/scale/offset, selection points, bounding boxes

const defaultState = {
    images: [] as Array<ImageDetails>,
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
    points: [] as Array<BackgroundPoint>,
    selectedLeaderIds: [] as Array<number>,
    comparisonDifference: {} as ComparisonDiff
}

export const useImageStateStore = defineStore("imageState", {
    state: () => ({ ...defaultState }),
    getters: {
        currentImage(state) {
            return state.images[state.currentImageIndex];
        }
    },
    actions: {
        reset() {
            Object.assign(this, defaultState);
            this.points = [];
            this.selectedLeaderIds = [];
            this.comparisonDifference = {};
            this.images = [];
        },

        addPoint(isPositive: boolean, x: number, y: number) {
            this.points.push({ positive: isPositive, position: [x, y] } as BackgroundPoint);
        },

        removeNearbyPoint(x: number, y: number, tolerance: number = 60) {
            if (this.points.length === 0) return;

            const closestPoint = this.points.reduce((a, b) =>
                distance(a.position[0], a.position[1], x, y) < distance(b.position[0], b.position[1], x, y) ? a : b
            );

            if (distance(closestPoint.position[0], closestPoint.position[1], x, y) < tolerance) {
                const pointIndex = this.points.findIndex((p) => p == closestPoint);
                this.points.splice(pointIndex, 1);
            }
        },

        clearResult() {
            this.comparisonDifference = {};
            this.currentImage.elements = [];
            this.currentImage.classifications = [];
        },

        clearSelections() {
            this.points = [];
            this.selectedLeaderIds = [];
        }
    }
});
