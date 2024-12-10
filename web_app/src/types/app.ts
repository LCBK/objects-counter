// Type definitions exclusively for the web application

import type { ImageWithAllData } from "./requests"

export interface ImageDetails {
    id: number,
    dataURL: string,
    width: number,
    height: number,
    backgroundMaskDataURL?: string,
    elements: Array<ImageElement>,
    selectedLeaderIds: Array<number>,
    points: Array<BackgroundPoint>
}

export interface ImageElement {
    id: number,
    topLeft: [number, number],
    bottomRight: [number, number],
    classificationName?: string,
    certainty?: number,
    isLeader?: boolean
}

export interface ObjectClassification {
    name: string,
    showBoxes: boolean
}

export interface BackgroundPoint {
    position: [number, number]
    positive: boolean                     // true - positive, false - negative
}

export interface ResultHistoryItem {
    id: number,
    images: Array<ImageWithAllData>,
    thumbnailUri?: string,
    timestamp: number
}

export interface ComparisonHistoryItem {
    id: number,
    images: Array<ImageWithAllData>,
    thumbnailUri?: string,
    timestamp: number,
    diff: { [key: string]: number },
    datasetName: string
}

export interface DatasetListItem {
    id: number,
    name: string,
    thumbnailUri?: string,
    timestamp: number,
    unfinished: boolean
}

export interface DatasetClassificationListItem {
    name: string,
    count: number
}

export interface RenameMapping {
    originalName: string,
    newName: string
}
