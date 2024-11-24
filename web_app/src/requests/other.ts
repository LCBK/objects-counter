import { config, endpoints } from "@/config";
import { useUserStateStore } from "@/stores/userState";
import { sendRequest } from "@/utils";


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
