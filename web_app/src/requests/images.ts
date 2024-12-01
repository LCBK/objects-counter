import { config, endpoints } from "@/config";
import { sendRequest } from "@/utils";
import type { BackgroundPoint } from "@/types/app";
import type {
    AcceptBackgroundClassifiedResponse,
    AcceptBackgroundNonClassifiedResponse,
    SendBackgroundPointsResponse,
    SendLeadersResponse,
    UploadImageResponse
} from "@/types/requests";


export async function getImageBlob(id: string | number) {
    const requestUri = config.serverUri + endpoints.getImage
        .replace("{image_id}", id.toString());

    const requestPromise = sendRequest(requestUri, null, "GET");
    const response = await requestPromise;

    if (response.ok) {
        return response.blob();
    }
    else {
        throw new Error(`Failed to get image ${id} blob`);
    }
}


export async function uploadImage(imageFile: File) {
    const requestUri = config.serverUri + endpoints.uploadImage;
    const requestData = new FormData();
    requestData.append("image", imageFile);

    const requestPromise = sendRequest(requestUri, requestData, "POST", "multipart/form-data");
    const response = await requestPromise;

    if (response.ok) {
        return response.json() as Promise<UploadImageResponse>;
    }
    else {
        throw new Error("Failed to upload image");
    }
}


export async function sendBackgroundPoints(id: string | number, points: Array<BackgroundPoint>) {
    const requestUri = config.serverUri + endpoints.sendSelection
        .replace("{image_id}", id.toString());
    const requestData = JSON.stringify({ data: points });

    const requestPromise = sendRequest(requestUri, requestData, "PUT");
    const response = await requestPromise;

    if (response.ok) {
        return response.json() as Promise<SendBackgroundPointsResponse>;
    }
    else {
        throw new Error(`Failed to send background points for image ${id}`);
    }
}


export async function acceptBackground(id: string | number, skip_classification: boolean = false) {
    const requestUri = config.serverUri + endpoints.acceptBackground
        .replace("{image_id}", id.toString());
    const requestData = JSON.stringify({ skip_classification: skip_classification });

    const requestPromise = sendRequest(requestUri, requestData, "POST");
    const response = await requestPromise;

    if (response.ok) {
        return response.json() as Promise<
            AcceptBackgroundClassifiedResponse | AcceptBackgroundNonClassifiedResponse
        >;
    }
    else {
        throw new Error("Failed to accept background");
    }
}
