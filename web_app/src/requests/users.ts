import { config, endpoints } from "@/config";
import { sendRequest } from "@/utils";
import type { UserLoginResponse } from "@/types/requests";


export async function loginUser(username: string, password: string) {
    const requestUri = config.serverUri + endpoints.userLogin;
    const requestData = JSON.stringify({ username: username, password: password });

    const requestPromise = sendRequest(requestUri, requestData, "POST");
    const response = await requestPromise;

    if (response.ok) {
        return response.json() as Promise<UserLoginResponse>;
    }
    else {
        if (response.status === 404) {
            throw new Error("Invalid username or password");
        }
        else {
            throw new Error("Failed to login");
        }
    }
}


export async function registerUser(username: string, password: string) {
    const requestUri = config.serverUri + endpoints.userRegister;
    const requestData = JSON.stringify({ username: username, password: password });

    const requestPromise = sendRequest(requestUri, requestData, "POST");
    const response = await requestPromise;

    if (!response.ok) {
        if (response.status === 400) {
            throw new Error("Invalid data or user already exists");
        }
        else {
            throw new Error("Failed to register");
        }
    }
}
