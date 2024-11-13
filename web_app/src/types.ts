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

export interface DatasetClassificationListItem {
    name: string,
    count: number
}


// Server response types
// TODO: Add more responses, ideally for each endpoint
export interface GetDatasetResponse {
    id: number,
    name: string,
    images: Array<any>
}


// Types used in server response interfaces
// TODO: If these types below will be used in other interfaces, make them generic
export interface DatasetResponseElement {
    id: number,
    top_left: [number, number],
    bottom_right: [number, number],
    certainty?: number,
    classification?: string
}

export interface DatasetResponseClassification {
    name: string,
    objects: Array<DatasetResponseElement>
}

export interface DatasetResponseImage {
    id: number,
    count: number,
    classifications: Array<DatasetResponseClassification>
}
