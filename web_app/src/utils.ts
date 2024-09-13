export async function sendRequest(
    uri: string, data: FormData | string, method: string = "POST", type: string = "application/json"
) : Promise<any> {
    try {
        const request: RequestInit = {
            method: method,
            body: data
        } 
        if (!(data instanceof FormData)) {
            request.headers = { "Content-Type": type };
        }
        const response = await fetch(uri, request);
        const result = await response.clone().json().catch(() => response.text());
        console.log(`Request to ${uri} succeeded. Result: `, result);
        return result;
    } catch (error) {
        return Promise.reject(`Request to ${uri} failed: ${error}`);
    }
}

export function distance(x1: number, y1: number, x2: number, y2: number) : number {
    return Math.sqrt(Math.pow(x1 - x2, 2) + Math.pow(y1 - y2, 2))
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
