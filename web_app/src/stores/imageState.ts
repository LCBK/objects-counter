import type { Point, Result } from "@/types";
import { distance } from "@/utils";
import { defineStore } from "pinia";


// Stores data related to user's image, e.g.: dimensions, canvas scale/offset, selection points, bounding boxes

const defaultState = {
    url: "",
    imageId: 0,
    width: 0,
    height: 0,
    scaledImageWidth: 0,
    scaledImageHeight: 0,
    overlayOffsetLeft: 0,
    overlayOffsetTop: 0,
    boundingBoxScale: 1,
    backgroundMaskDataURL: "",
    isPanning: false,
    userZoom: 1,
    results: [] as Array<Result>,
    points: [] as Array<Point>
}

export const useImageStateStore = defineStore("imageState", {
    state: () => ({ ...defaultState }),
    actions: {
        reset() {
            Object.assign(this, defaultState);
            this.points = []
        },

        addPoint(isPositive: boolean, x: number, y: number) {
            this.points.push({ isPositive: isPositive, position: [x, y] } as Point);
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
            this.results = [];
        }
    }
});
