// Type definitions for responses from the API
// Properties are named in snake_case, as they are received from the server

import type { BackgroundPoint } from "./app";


// Images

export type UploadImageResponse = number;

export interface SendBackgroundPointsResponse {
    mask: Array<Array<boolean>>
}

export interface AcceptBackgroundClassifiedResponse {
    id: number,
    classifications: Array<ClassificationWithObjects>,
    count: number
}

export interface AcceptBackgroundNonClassifiedResponse {
    id: number,
    background_points: {
        data: Array<BackgroundPoint>
    },
    elements: Array<ImageElement>,
    timestamp: string
}

export type SendLeadersResponse = string;


// Datasets

export interface GetDatasetResponse {
    id: number,
    name: string,
    images: Array<any>          // TODO: type
}

export interface GetDatasetsResponse extends Array<{
    id: number,
    name: string,
    timestamp: string,
    images: Array<any>,         // TODO: type
    unfinished: boolean,
    user: string
}> { }

export type CreateDatasetResponse = string;

export interface RenameDatasetResponse {
    id: number,
    name: string,
    timestamp: string,
    images: Array<any>,         // TODO: type
    unfinished: boolean,
    user: string
}


// Results

export interface GetResultResponse {
    data: {
        classifications: Array<any>,        // TODO: type
        count: number
    },
    id: number,
    image_id: number,
    timestamp: string,
    user: string
}

export interface GetResultsResponse extends Array<GetResultResponse> { }


// Users

export interface UserLoginResponse {
    id: number,
    username: string,
    token: string
}


// Common

export interface GetThumbnailsResponse extends Array<{
    id: number,
    thumbnail: string
}> { }


// Intermediate types

export interface ImageElement {
    id: number,
    top_left: [number, number],
    bottom_right: [number, number],
    certainty?: number,
    classification?: string
}

export interface ClassificationWithObjects {
    name: string,
    objects: Array<ImageElement>
}
