export const config = {
    serverUri: "http://localhost:5000"
};

export const endpoints = {
    uploadImage: "/api/upload",
    sendSelection: "/api/images/{image_id}/background",
    acceptBackground: "/api/images/{image_id}/background/accept"
};

export const boundingBoxColors = [
    "#ff595e", "#ff924c", "#ffca3a", "#c5ca30", "#8ac926", "#52a675", "#1982c4", "#4267ac", "#6a4c93"
]
