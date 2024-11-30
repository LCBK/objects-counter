import { boundingBoxColors, config } from "./config";
import { useUserStateStore } from "./stores/userState";
import { useImageStateStore } from "./stores/imageState";
import type { ClassificationWithObjects, GetDatasetResponse, ImageElementResponse } from "./types/requests";
import type { DatasetClassificationListItem, ImageElement } from "./types/app";


export async function sendRequest(
    uri: string, data: FormData | string | null, method: string, type: string = "application/json"
): Promise<globalThis.Response> {
    const headers = new Headers();

    if (!(data instanceof FormData)) {
        headers.append("Content-Type", type);
    }

    const userState = useUserStateStore();
    if (userState.isLoggedIn) {
        headers.append("Authorization", userState.userToken);
    }

    const request: RequestInit = {
        method: method,
        body: data,
        headers: headers
    }

    try {
        const response = await fetch(uri, request);

        if (config.logResponses) {
            // Clone responses to avoid consuming the original one
            const jsonResponse = response.clone();
            const textResponse = response.clone();
            console.log(
                `Response from ${uri} (${response.status}): `,
                jsonResponse.json().catch(() => textResponse.text())
            );
        }

        return response;
    }
    catch (error) {
        return Promise.reject(`Request to ${method} ${uri} failed: ${error}`);
    }
}


export function distance(x1: number, y1: number, x2: number, y2: number): number {
    return Math.sqrt(Math.pow(x1 - x2, 2) + Math.pow(y1 - y2, 2))
}


export function formatClassificationName(name: string): string {
    return /^\d*$/.test(name) ? "Type " + name : name;
}


export function createMaskImage(mask: Array<Array<boolean>>): ImageData {
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


export function parseClassificationsFromResponse(classifications: Array<ClassificationWithObjects>): void {
    const imageState = useImageStateStore();

    classifications.forEach((classification, index: number) => {
        imageState.classifications.push({
            index: index,
            name: classification.name,
            count: classification.objects.length,
            showBoxes: true,
            boxColor: boundingBoxColors[index % boundingBoxColors.length]
        });

        classification.objects.forEach((element) => {
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


export function parseClassificationsFromElementsResponse(elements: Array<ImageElementResponse>): void {
    const imageState = useImageStateStore();
    const classifications = [] as Array<string>;

    elements.forEach((element) => {
        if (element.classification && !classifications.includes(element.classification)) {
            classifications.push(element.classification);
        }
    });

    classifications.sort();
    classifications.forEach((classification, index) => {
        const classificationElements = elements.filter((element) => element.classification === classification);
        imageState.classifications.push({
            index: index,
            name: classification,
            count: classificationElements.length,
            showBoxes: true,
            boxColor: boundingBoxColors[index % boundingBoxColors.length]
        });

        classificationElements.forEach((element) => {
            imageState.imageElements.push({
                id: element.id,
                topLeft: element.top_left,
                bottomRight: element.bottom_right,
                certainty: element.certainty,
                classificationIndex: index
            });
        });
    });
}


export function parseElementsFromResponse(elements: Array<ImageElementResponse>): void {
    const imageState = useImageStateStore();
    for (const element of elements) {
        imageState.imageElements.push({
            id: element.id,
            topLeft: element.top_left,
            bottomRight: element.bottom_right
        });
    }
}


export function getClassificationsFromDataset(dataset: GetDatasetResponse): Array<DatasetClassificationListItem> {
    const classificationItems = [] as Array<DatasetClassificationListItem>;

    dataset.images.forEach(image => {
        image.elements.forEach(element => {
            if (!element.classification) return;
            if (!classificationItems.some(classification => classification.name === element.classification)) {
                classificationItems.push({
                    name: element.classification,
                    count: 1
                });
            }
            else {
                const classification = classificationItems.find(c => c.name === element.classification);
                if (classification) classification.count++;
            }
        });
    });

    return classificationItems;
}


export function processImageFile(imageFile: File): void {
    const imageState = useImageStateStore();

    const url = window.URL.createObjectURL(imageFile);
    // TODO: Move to imageBatch along with id and maybe some other data?
    imageState.imageDataURL = url;           // For displaying the image

    const img = new Image;
    img.src = url;
    img.onload = () => {
        imageState.width = img.width;
        imageState.height = img.height;
    };
}


export function base64ToImageUri(base64: string): string {
    return "data:image/png;base64," + base64;
}


export function isUserAgentMobile(): boolean {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}
