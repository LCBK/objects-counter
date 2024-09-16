export interface ImageElement {
    index: number,
    top_left: [number, number],
    bottom_right: [number, number],
    classification: string,
    certainty: number,
    color: string
}

export interface ObjectQuantity {
    index: number,
    classification: string,
    count: number
}

export interface BackgroundPoint {
    isPositive: boolean,                  // true - positive, false - negative
    position: [number, number]
}
