export interface Result {
    index: number,
    top_left: [number, number],
    bottom_right: [number, number],
    certainty: number,
    class: string,
    color: string
}
