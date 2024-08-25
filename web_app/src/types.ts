export interface Result {
    index: number,
    top_left: [number, number],
    bottom_right: [number, number],
    certainty: number,
    class: string,
    color: string
}

export interface Quantity {
    index: number,
    class: string,
    count: number
}

export interface Point {
    isPositive: boolean,                  // true - positive, false - negative
    position: [number, number]
}
