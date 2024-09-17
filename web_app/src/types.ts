export interface ImageElement {
    topLeft: [number, number],
    bottomRight: [number, number],
    certainty: number,
    classification: string,
    classificationIndex: number
}

export interface ObjectClassification {
    index: number,
    classificationName: string,
    count: number,
    isNameAssigned: boolean,                // Determines whether the user named the classification or not
    showBoxes: boolean,
    boxColor: string
}

export interface BackgroundPoint {
    position: [number, number]
    positive: boolean,                    // true - positive, false - negative
}
