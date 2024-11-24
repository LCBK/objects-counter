import { config, endpoints } from "@/config";
import { sendRequest } from "@/utils";
import type {
    CreateDatasetResponse,
    GetDatasetResponse,
    GetDatasetsResponse,
    GetThumbnailsResponse,
    RenameDatasetResponse
} from "@/types/responses";


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


export async function createDataset(name: string) {
    const requestUri = config.serverUri + endpoints.createDataset;
    const requestData = JSON.stringify({ name: name });

    const requestPromise = sendRequest(requestUri, requestData, "POST");
    const response = await requestPromise;

    if (response.ok) {
        return response.json() as Promise<CreateDatasetResponse>;
    }
    else {
        throw new Error(`Failed to create dataset ${name}`);
    }
}


export async function renameDataset(id: string | number, name: string) {
    const requestUri = config.serverUri + endpoints.renameDataset
        .replace("{dataset_id}", id.toString());
    const requestData = JSON.stringify({ name: name });

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
    // TODO: type
    datasetId: string | number, imageId: string | number, classifications: any
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
        return response.json();         // TODO: type
    }
    else {
        throw new Error(`Failed to adjust classifications for dataset ${datasetId} image ${imageId}`);
    }
}


export async function addImageToDataset(
    // TODO: type
    datasetId: string | number, imageId: string | number, classifications: Array<any>
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
        return response.json();         // TODO: type
    }
    else {
        throw new Error(`Failed to add image ${imageId} to dataset ${datasetId}`);
    }
}


export async function compareToDataset(datasetId: string | number, imageIds: Array<string | number>) {
    const requestUri = config.serverUri + endpoints.compareToDataset
        .replace("{dataset_id}", datasetId.toString());
    const requestData = JSON.stringify({ image_ids: imageIds });

    const requestPromise = sendRequest(requestUri, requestData, "POST");
    const response = await requestPromise;

    if (response.ok) {
        return response.json();         // TODO: type
    }
    else {
        throw new Error(`Failed to compare dataset ${datasetId}`);
    }
}
