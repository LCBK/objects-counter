export const config = {
    // Backend communication
    serverUri: "http://" + import.meta.env.VITE_BACKEND_ADDRESS,
    serverIsAliveDelay: 1500,           // [ms]
    serverIsAliveTimeout: 5000,         // [ms]

    // Layout, display
    displayClassifications: true,
    displayCertainty: false,

    // User validation
    minUsernameLength: 4,
    maxUsernameLength: 255,
    minPasswordLength: 8,
    maxPasswordLength: 255,
    requirePasswordLowerChar: true,
    requirePasswordUpperChar: true,
    requirePasswordDigit: true,
    requirePasswordSymbol: true,

    // Other
    logResponses: true         // Can leak JWT token
};

export const endpoints = {
    isAlive: "/api/is-alive",
    uploadImage: "/api/upload",
    sendSelection: "/api/images/{image_id}/background",
    acceptBackground: "/api/images/{image_id}/background/accept",
    userRegister: "/api/users/register",
    userLogin: "/api/users/login",
    results: "/api/results/",
    compareElements: "/api/images/compare",
    renameClassification: "/api/results/{result_id}/classification/{classification_name}/rename"
};

export const boundingBoxColors = [
    "#ff595e", "#ff924c", "#ffca3a", "#c5ca30", "#8ac926", "#52a675", "#1982c4", "#4267ac", "#6a4c93"
];

export const themeUrls = {
    dark: "https://cdn.jsdelivr.net/npm/primevue@3.50.x/resources/themes/aura-dark-blue/theme.css",
    light: "https://cdn.jsdelivr.net/npm/primevue@3.50.x/resources/themes/aura-light-blue/theme.css"
}
