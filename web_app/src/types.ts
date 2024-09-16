export interface ImageElement {
    topLeft: [number, number],
    bottomRight: [number, number],
    classification: string,
    certainty: number,
    color: string
}

export interface ObjectClassification {
    classification: string,
    count: number,
    isNameAssigned: boolean                 // Determines whether the user named the classification or not
}

export interface BackgroundPoint {
    isPositive: boolean,                    // true - positive, false - negative
    position: [number, number]
}
