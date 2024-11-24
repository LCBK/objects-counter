import { config, endpoints } from "@/config";
import { sendRequest } from "@/utils";
import type {
    GetResultResponse,
    GetResultsResponse,
    GetThumbnailsResponse
} from "@/types/responses";


export async function getResult(id: string | number) {
    const resultRequestUri = config.serverUri + endpoints.getResult
        .replace("{result_id}", id.toString());

    const resultRequestPromise = sendRequest(resultRequestUri, null, "GET");
    const response = await resultRequestPromise;

    if (response.ok) {
        return response.json() as Promise<GetResultResponse>;
    }
    else {
        throw new Error(`Failed to get result ${id}`);
    }
}


export async function getResults() {
    const resultsRequestUri = config.serverUri + endpoints.getResults;

    const resultsRequestPromise = sendRequest(resultsRequestUri, null, "GET");
    const response = await resultsRequestPromise;

    if (response.ok) {
        return response.json() as Promise<GetResultsResponse>;
    }
    else {
        throw new Error("Failed to get results");
    }
}


export async function getResultsThumbnails() {
    const requestUri = config.serverUri + endpoints.getResultsThumbnails;

    const requestPromise = sendRequest(requestUri, null, "GET");
    const response = await requestPromise;

    if (response.ok) {
        return response.json() as Promise<GetThumbnailsResponse>;
    }
    else {
        throw new Error(`Failed to get results thumbnails`);
    }
}


export async function renameResultClassification(
    id: string | number, oldName: string, newName: string
): Promise<string> {
    const requestUri = config.serverUri + endpoints.renameClassification
        .replace("{result_id}", id.toString())
        .replace("{classification_name}", oldName);
    const requestData = newName;

    const requestPromise = sendRequest(requestUri, requestData, "POST");
    const response = await requestPromise;

    if (response.ok) {
        return response.json();
    }
    else {
        throw new Error(`Failed to rename classification ${oldName} to ${newName} for id ${id}`);
    }
}


export async function deleteResult(id: string | number) {
    const requestUri = config.serverUri + endpoints.deleteResult
        .replace("{result_id}", id.toString());

    const requestPromise = sendRequest(requestUri, null, "DELETE");
    const response = await requestPromise;

    if (response.ok) {
        return;
    }
    else {
        throw new Error(`Failed to delete result ${id}`);
    }
}
