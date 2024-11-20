import { boundingBoxColors, config, endpoints } from "./config";
import { useUserStateStore } from "./stores/userState";
import { useImageStateStore } from "./stores/imageState";
import type { DatasetClassificationListItem, DatasetResponseClassification, GetDatasetResponse, ImageElement, ObjectClassification } from "./types";


export interface Response {
    data: any,
    status: number
}


export async function sendRequest(
    uri: string, data: FormData | string | null, method: string = "POST",
    requestType: string = "application/json", toJson: boolean = true
) : Promise<Response> {
    try {
        const userState = useUserStateStore();

        const request: RequestInit = {
            method: method,
            body: data
        }

        const requestHeaders: HeadersInit = new Headers();
        if (!(data instanceof FormData)) {
            requestHeaders.append("Content-Type", requestType);
        }
        if (userState.isLoggedIn) {
            requestHeaders.append("Authorization", userState.userToken);
        }
        request.headers = requestHeaders;

        const response = await fetch(uri, request);
        let result;
        if (toJson) {
            result = await response.clone().json().catch(() => response.text());
        }
        else {
            result = await response;
        }

        if (config.logResponses) {
            console.log(`Response for request to ${uri} (${response.status}): `, result);
        }

        return { data: result, status: response.status };
    } catch (error) {
        return Promise.reject(`Request to ${uri} failed: ${error}`);
    }
}


export function distance(x1: number, y1: number, x2: number, y2: number) : number {
    return Math.sqrt(Math.pow(x1 - x2, 2) + Math.pow(y1 - y2, 2))
}


export function formatClassificationName(name: string) : string {
    return /^\d*$/.test(name) ? "Type " + name : name;
}


export function createMaskImage(mask: Array<Array<boolean>>) : ImageData {
    const width = mask[0].length;
    const height = mask.length;
    const buffer = new Uint8ClampedArray(width * height * 4);

    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const pos = (y * width + x) * 4;
            buffer[pos] = Number(mask[y][x]) * 255;
            buffer[pos + 1] = Number(mask[y][x]) * 255;
            buffer[pos + 2] = Number(mask[y][x]) * 255;
            buffer[pos + 3] = Number(mask[y][x]) * 255;
        }
    }

    const imageData = new ImageData(buffer, width, height);
    return imageData;
}


export function parseClassificationsFromResponse(classifications: Array<any>) : void {
    const imageState = useImageStateStore();

    classifications.forEach((classification: any, index: number) => {
        imageState.objectClassifications.push({
            index: index,
            classificationName: classification.name,
            count: classification.objects.length,
            showBoxes: true,
            boxColor: boundingBoxColors[index % boundingBoxColors.length]
        });

        classification.objects.forEach((element: any) => {
            const imageElement = {
                id: element.id,
                topLeft: element.top_left,
                bottomRight: element.bottom_right,
                certainty: element.certainty,
                classificationIndex: index
            } as ImageElement;

            for (const leaderId of imageState.selectedLeaderIds) {
                if (leaderId === element.id) {
                    imageElement.isLeader = true;
                    break;
                }
            }

            imageState.imageElements.push(imageElement);
        });
    });
}


export function parseElementsFromResponse(elements: Array<any>) : void {
    const imageState = useImageStateStore();
    for (const element of elements) {
        imageState.imageElements.push({
            id: element.id,
            topLeft: element.top_left,
            bottomRight: element.bottom_right
        });
    }
}


export function getClassificationsFromDataset(dataset: GetDatasetResponse) : Array<DatasetClassificationListItem> {
    const classifications = [] as Array<DatasetResponseClassification>;

    // Merge classifications from all images
    dataset.images.forEach(image => {
        image.classifications.forEach((classification: DatasetResponseClassification) => {
            const existingClassification = classifications.find(c => c.name === classification.name);
            if (existingClassification) {
                existingClassification.objects.push(...classification.objects);
            }
            else {
                classifications.push({ name: classification.name, objects: classification.objects });
            }
        });
    });

    const classificationList = classifications.map((classification: DatasetResponseClassification) => {
        return {
            name: classification.name,
            count: classification.objects.length
        } as DatasetClassificationListItem;
    });
    return classificationList;
}


export function checkServerStatus() : Promise<boolean> {
    return new Promise((resolve) => {
        sendRequest(config.serverUri + endpoints.isAlive, null, "GET")
            .then(response => {
                if (response.status === 200) {
                    resolve(true);
                } else if (response.status === 401) {
                    const userState = useUserStateStore();
                    userState.logout();
                    resolve(true);
                } else {
                    resolve(false);
                }
            })
            .catch(() => resolve(false));
    });
}


export function base64ToImageUri(base64: string) : string {
    return "data:image/png;base64," + base64;
}


export function isUserAgentMobile() : boolean {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}
