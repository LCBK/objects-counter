import { boundingBoxColors, config } from "./config";
import { useUserStateStore } from "./stores/userState";
import { useImageStateStore } from "./stores/imageState";
import type { ClassificationWithObjects, GetDatasetResponse, ImageElementResponse, ImageWithAllData } from "./types/requests";
import type { DatasetClassificationListItem, ImageDetails, ImageElement, ObjectClassification } from "./types/app";


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


export function getImageClassifications(id: number): Array<ObjectClassification> {
    const imageState = useImageStateStore();
    const classifications = [] as Array<ObjectClassification>;
    const image = imageState.images.find(image => image.id === id);

    if (!image) return classifications;

    for (const element of image.elements) {
        if (element.classificationName) {
            if (!classifications.find(c => c.name === element.classificationName)) {
                classifications.push({
                    name: element.classificationName,
                    showBoxes: true
                });
            }
        }
    }

    return classifications;
}


export function getClassificationBoxColor(name: string): string {
    const imageState = useImageStateStore();
    const classificationIndex = imageState.classifications.findIndex(c => c.name === name);

    if (classificationIndex === -1) return boundingBoxColors[0];
    return boundingBoxColors[classificationIndex % boundingBoxColors.length];
}


// TODO: Merge with parseClassificationsFromResponse when implementing multiple images on simple counting
export function parseMultipleClassificationsFromResponse(images: Array<ImageWithAllData>): void {
    images.forEach(image => parseElementsToImage(image.id, image.elements));
}


export function parseClassificationsFromResponse(classifications: Array<ClassificationWithObjects>): void {
    const imageState = useImageStateStore();

    classifications.forEach(classification => {
        if (!imageState.classifications.find(c => c.name === classification.name)) {
            // If received classification name is found in the rename map, use the new name
            const mapping = imageState.classificationRenameMap.find(c => c.originalName === classification.name);
            if (mapping) classification.name = mapping.newName;
            else imageState.addClassification(classification.name);
        }

        classification.objects.forEach(element => {
            const imageElement = {
                id: element.id,
                topLeft: element.top_left,
                bottomRight: element.bottom_right,
                certainty: element.certainty,
                classificationName: classification.name
            } as ImageElement;

            for (const leaderId of imageState.currentImage.selectedLeaderIds) {
                if (leaderId === element.id) {
                    imageElement.isLeader = true;
                    break;
                }
            }

            imageState.currentImage.elements.push(imageElement);
        });
    });

    imageState.sortClassifications();
}


export function parseElementsToImage(imageId: number, elements: Array<ImageElementResponse>): void {
    const imageState = useImageStateStore();

    const image = imageState.images.find(image => image.id === imageId);
    if (!image) return;

    elements.forEach(element => {
        if (element.classification && !imageState.classifications.find(c => c.name === element.classification)) {
            // If received classification name is found in the rename map, use the new name
            const mapping = imageState.classificationRenameMap.find(c => c.originalName === element.classification);
            if (mapping) element.classification = mapping.newName;
            else imageState.addClassification(element.classification);
        }

        image.elements.push({
            id: element.id,
            topLeft: element.top_left,
            bottomRight: element.bottom_right,
            certainty: element.certainty,
            classificationName: element.classification
        });
    });

    imageState.sortClassifications();
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


export async function processImageData(source: File | Blob, id: number): Promise<void> {
    const imageState = useImageStateStore();

    const url = window.URL.createObjectURL(source);
    const img = new Image;
    img.src = url;

    return img.decode().then(() => {
        const imageDetails = {
            id: id,
            dataURL: url,
            width: img.width,
            height: img.height,
            elements: [],
            selectedLeaderIds: [],
            points: []
        } as ImageDetails;

        imageState.images.push(imageDetails);
    });
}


export function base64ToImageUri(base64: string): string {
    return "data:image/png;base64," + base64;
}


export function isUserAgentMobile(): boolean {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}
