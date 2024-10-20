export interface ImageElement {
    topLeft: [number, number],
    bottomRight: [number, number],
    certainty: number,
    classificationIndex: number
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
    imageUri?: string,
    timestamp: number,
    classificationCount: number,
    elementCount: number
}
