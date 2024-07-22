import type { Point, Result } from "@/types";
import { distance } from "@/utils";
import { defineStore } from "pinia";


const defaultState = {
    url: "",
    width: 0,
    height: 0,
    scaledImageWidth: 0,
    scaledImageHeight: 0,
    overlayOffsetLeft: 0,
    overlayOffsetTop: 0,
    boundingBoxScale: 1,
    results: [] as Array<Result>,
    points: [] as Array<Point>
}

export const useImageStateStore = defineStore("imageState", {
    state: () => ({ ...defaultState }),
    actions: {
        reset() {
            Object.assign(this, defaultState);
        },

        addPoint(isPositive: boolean, x: number, y: number) {
            this.points.push({ isPositive: isPositive, position: [x, y] } as Point);
        },

        removePoint(x: number, y: number) {
            const closestPoint = this.points.reduce((a, b) => 
                distance(a.position[0], a.position[1], x, y) < distance(b.position[0], b.position[1], x, y) ? a : b
            );

            const distanceTolerance = 40;
            if (distance(closestPoint.position[0], closestPoint.position[1], x, y) < distanceTolerance) {
                const pointIndex = this.points.findIndex((p) => p == closestPoint);
                this.points.splice(pointIndex, 1);
            }
        }
    }
});
