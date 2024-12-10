import { config, endpoints } from "@/config";
import type {
    CompareToDatasetResponse,
    GetComparisonHistoryResponse,
    GetThumbnailsResponse
} from "@/types/requests";
import { sendRequest } from "@/utils";



export async function compareToDataset(datasetId: string | number, imageIds: Array<string | number>) {
    const requestUri = config.serverUri + endpoints.compareToDataset
        .replace("{dataset_id}", datasetId.toString());
    const requestData = JSON.stringify({ image_ids: imageIds });

    const requestPromise = sendRequest(requestUri, requestData, "POST");
    const response = await requestPromise;

    if (response.ok) {
        return response.json() as Promise<CompareToDatasetResponse>;
    }
    else {
        throw new Error(`Failed to compare dataset ${datasetId}`);
    }
}


export async function getComparisonHistory() {
    const requestUri = config.serverUri + endpoints.getComparisonHistory;

    const requestPromise = sendRequest(requestUri, null, "GET");
    const response = await requestPromise;

    if (response.ok) {
        return response.json() as Promise<GetComparisonHistoryResponse>;
    }
    else {
        throw new Error("Failed to get comparison history");
    }
}


export async function deleteComparison(id: string | number) {
    const requestUri = config.serverUri + endpoints.deleteComparison
        .replace("{comparison_id}", id.toString());

    const requestPromise = sendRequest(requestUri, null, "DELETE");
    const response = await requestPromise;

    if (!response.ok) {
        throw new Error("Failed to delete comparison");
    }
}


export async function getComparisonHistoryThumbnails() {
    const requestUri = config.serverUri + endpoints.getComparisonHistoryThumbnails;

    const requestPromise = sendRequest(requestUri, null, "GET");
    const response = await requestPromise;

    if (response.ok) {
        return response.json() as Promise<GetThumbnailsResponse>;
    }
    else {
        throw new Error("Failed to get comparison history thumbnails");
    }
}
