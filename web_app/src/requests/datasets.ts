import { config, endpoints } from "@/config";
import { sendRequest } from "@/utils";
import type {
    AddImageToDatasetRequestData,
    AddImageToDatasetResponse,
    AdjustClassificationsRequestData,
    AdjustClassificationsResponse,
    CreateDatasetResponse,
    GetDatasetResponse,
    GetDatasetsResponse,
    GetThumbnailsResponse,
    RenameDatasetResponse
} from "@/types/requests";


export async function getDataset(id: string | number) {
    const requestUri = config.serverUri + endpoints.getDataset
        .replace("{dataset_id}", id.toString());

    const requestPromise = sendRequest(requestUri, null, "GET");
    const response = await requestPromise;

    if (response.ok) {
        return response.json() as Promise<GetDatasetResponse>;
    }
    else {
        throw new Error(`Failed to get dataset ${id}`);
    }
}


export async function getDatasets() {
    const requestUri = config.serverUri + endpoints.getDatasets;

    const requestPromise = sendRequest(requestUri, null, "GET");
    const response = await requestPromise;

    if (response.ok) {
        return response.json() as Promise<GetDatasetsResponse>;
    }
    else {
        throw new Error("Failed to get datasets");
    }
}


export async function getDatasetsThumbnails() {
    const requestUri = config.serverUri + endpoints.getDatasetsThumbnails;

    const requestPromise = sendRequest(requestUri, null, "GET");
    const response = await requestPromise;

    if (response.ok) {
        return response.json() as Promise<GetThumbnailsResponse>;
    }
    else {
        throw new Error(`Failed to get datasets thumbnails`);
    }
}


export async function createDataset(name: string, unfinished: boolean = false) {
    const requestUri = config.serverUri + endpoints.createDataset;
    const requestData = JSON.stringify({
        name: name,
        unfinished: unfinished
    });

    const requestPromise = sendRequest(requestUri, requestData, "POST");
    const response = await requestPromise;

    if (response.ok) {
        return response.json() as Promise<CreateDatasetResponse>;
    }
    else {
        throw new Error(`Failed to create dataset ${name}`);
    }
}


export async function renameDataset(id: string | number, name: string, unfinished: boolean = false) {
    const requestUri = config.serverUri + endpoints.renameDataset
        .replace("{dataset_id}", id.toString());
    const requestData = JSON.stringify({
        name: name,
        unfinished: unfinished
    });

    const requestPromise = sendRequest(requestUri, requestData, "PATCH");
    const response = await requestPromise;

    if (response.ok) {
        return response.json() as Promise<RenameDatasetResponse>;
    }
    else {
        throw new Error(`Failed to rename dataset ${id} to ${name}`);
    }
}


export async function deleteDataset(id: string | number) {
    const requestUri = config.serverUri + endpoints.deleteDataset
        .replace("{dataset_id}", id.toString());

    const requestPromise = sendRequest(requestUri, null, "DELETE");
    const response = await requestPromise;

    if (response.ok) {
        return;
    }
    else {
        throw new Error(`Failed to delete dataset ${id}`);
    }
}


export async function adjustClassifications(
    datasetId: string | number, imageId: string | number, classifications: AdjustClassificationsRequestData
) {
    const requestUri = config.serverUri + endpoints.adjustDatasetClassifications
        .replace("{dataset_id}", datasetId.toString())
        .replace("{image_id}", imageId.toString());
    const requestData = JSON.stringify({
        classifications: classifications
    });

    const requestPromise = sendRequest(requestUri, requestData, "PATCH");
    const response = await requestPromise;

    if (response.ok) {
        return response.json() as Promise<AdjustClassificationsResponse>;
    }
    else {
        throw new Error(`Failed to adjust classifications for dataset ${datasetId} image ${imageId}`);
    }
}


export async function addImageToDataset(
    datasetId: string | number, imageId: string | number, classifications: AddImageToDatasetRequestData
) {
    const requestUri = config.serverUri + endpoints.addImageToDataset
        .replace("{dataset_id}", datasetId.toString());
    const requestData = JSON.stringify({
        image_id: imageId,
        classifications: classifications
    });


    const requestPromise = sendRequest(requestUri, requestData, "POST");
    const response = await requestPromise;

    if (response.ok) {
        return response.json() as Promise<AddImageToDatasetResponse>;
    }
    else {
        throw new Error(`Failed to add image ${imageId} to dataset ${datasetId}`);
    }
}
