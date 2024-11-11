export interface ImageElement {
    id: number,
    topLeft: [number, number],
    bottomRight: [number, number],
    certainty?: number,
    classificationIndex?: number,
    isLeader?: boolean
}

export interface ObjectClassification {
    index: number,
    classificationName: string,
    count: number,
    showBoxes: boolean,
    boxColor: string
}

export interface BackgroundPoint {
    position: [number, number]
    positive: boolean,                    // true - positive, false - negative
}

export interface ResultHistoryItem {
    id: number,
    imageId: number,
    thumbnailUri?: string,
    timestamp: number,
    classificationCount: number,
    elementCount: number
}

export interface DatasetListItem {
    id: number,
    name: string,
    thumbnailUri?: string,
    timestamp: number
}
