// Type definitions for requests and responses from the API
// Properties are named in snake_case, as they are received from the server

import type { BackgroundPoint } from "./app";


// Images

export type UploadImageResponse = number;

export interface SendBackgroundPointsResponse {
    mask: Array<Array<boolean>>
}

export type AcceptBackgroundResponse = ImageWithAllData;

export type SendLeadersResponse = string;

export interface AdjustClassificationsRequestData extends Array<{
    name: string,
    elements: Array<number>
}> { }

export type AdjustClassificationsResponse = ImageWithClassifications;


// Datasets

export interface GetDatasetResponse {
    id: number,
    name: string,
    timestamp: string,
    images: Array<ImageWithAllData>,
    unfinished: boolean,
    user: string
}

export type GetDatasetsResponse = Array<GetDatasetResponse>;

export type CreateDatasetResponse = string;

export type RenameDatasetResponse = GetDatasetResponse;

export interface AddImageToDatasetRequestData extends Array<{
    name: string | number,
    leader_id: number
}> { }

export type AddImageToDatasetResponse = GetDatasetResponse;


// Results

export interface GetResultResponse {
    id: number,
    images: Array<ImageWithAllData>,
    timestamp: string,
    user: string
}

export interface GetResultsResponse extends Array<GetResultResponse> { }

export type CreateResultResponse = GetResultResponse;


// Comparisons

export interface GetComparisonResponse {
    id: number,
    dataset: GetDatasetResponse,
    images: Array<ImageWithAllData>,
    diff: ComparisonDiff,
    timestamp: string,
    user: string
}

export interface ComparisonDiff {
    [key: string]: number
}

export type CompareToDatasetResponse = GetComparisonResponse;

export type GetComparisonHistoryResponse = Array<GetComparisonResponse>;


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

export interface ImageElementResponse {
    id: number,
    top_left: [number, number],
    bottom_right: [number, number],
    certainty?: number,
    classification?: string
}

export interface ClassificationWithObjects {
    name: string,
    objects: Array<ImageElementResponse>
}

export interface ImageWithClassifications {
    id: number,
    classifications: Array<ClassificationWithObjects>,
    count: number
}

export interface ImageWithAllData {
    id: number,
    background_points: {
        data: Array<BackgroundPoint>
    },
    elements: Array<ImageElementResponse>,
    timestamp: string
}
