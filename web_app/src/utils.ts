export async function sendRequest(uri: string, data: FormData, method: string = "POST") : Promise<any> {
    try {
        const response = await fetch(uri, {
            method: method,
            body: data,
        });
        const result = await response.json();
        console.log(`Request to ${uri} succeeded. Result: `, result);
        return result;
    } catch (error) {
        return Promise.reject(`Request to ${uri} failed: ${error}`);
    }
}
