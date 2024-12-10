export const config = {
    // Backend communication
    serverAddress: import.meta.env.VITE_BACKEND_ADDRESS,
    serverUseHttps: false,
    get serverUri() {
        return (this.serverUseHttps ? "https://" : "http://") + this.serverAddress;
    },
    serverIsAliveDelay: 1500,           // [ms]
    serverIsAliveTimeout: 5000,         // [ms]

    // User validation
    minUsernameLength: 4,
    maxUsernameLength: 255,
    minPasswordLength: 8,
    maxPasswordLength: 255,
    requirePasswordLowerChar: true,
    requirePasswordUpperChar: true,
    requirePasswordDigit: true,
    requirePasswordSymbol: true,

    // Debug
    logResponses: true,                 // Can leak JWT token
    showDebugSettings: false
};


export const endpoints = {
    isAlive: "/api/is-alive",
    uploadImage: "/api/images/upload",
    getImage: "/api/images/{image_id}",
    sendSelection: "/api/images/{image_id}/background",
    acceptBackground: "/api/images/{image_id}/background/accept",
    userRegister: "/api/users/register",
    userLogin: "/api/users/login",
    getResults: "/api/results/",
    getResult: "/api/results/{result_id}",
    getResultsThumbnails: "/api/results/thumbnails",
    deleteResult: "/api/results/{result_id}",
    renameClassification: "/api/results/{result_id}/classification/{classification_name}/rename",
    getDatasets: "/api/datasets/",
    getDataset: "/api/datasets/{dataset_id}",
    createDataset: "/api/datasets/",
    deleteDataset: "/api/datasets/{dataset_id}",
    renameDataset: "/api/datasets/{dataset_id}",
    getDatasetImages: "/api/datasets/{dataset_id}/images",
    addImageToDataset: "/api/datasets/{dataset_id}/images",
    getDatasetsThumbnails: "/api/datasets/thumbnails",
    adjustDatasetClassifications: "/api/datasets/{dataset_id}/images/{image_id}",
    compareToDataset: "/api/datasets/{dataset_id}/comparison",
    getComparisonHistory: "/api/comparison_history/",
    getComparisonHistoryThumbnails: "/api/comparison_history/thumbnails",
    deleteComparison: "/api/comparison_history/{comparison_id}"
};


export const boundingBoxColors = [
    "#ff595e",
    "#ff924c",
    "#ffca3a",
    "#c5ca30",
    "#8ac926",
    "#52a675",
    "#1982c4",
    "#4267ac",
    "#6a4c93"
];


export const themeUrls = {
    dark: "https://cdn.jsdelivr.net/npm/primevue@3.50.x/resources/themes/aura-dark-blue/theme.css",
    light: "https://cdn.jsdelivr.net/npm/primevue@3.50.x/resources/themes/aura-light-blue/theme.css"
};
