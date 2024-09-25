export const config = {
    // Backend communication
    serverUri: "http://" + import.meta.env.VITE_BACKEND_ADDRESS,

    // User validation
    minUsernameLength: 4,
    maxUsernameLength: 255,
    minPasswordLength: 8,
    maxPasswordLength: 255,
    requirePasswordLowerChar: true,
    requirePasswordUpperChar: true,
    requirePasswordDigit: true,
    requirePasswordSymbol: true,
};

export const endpoints = {
    uploadImage: "/api/upload",
    sendSelection: "/api/images/{image_id}/background",
    acceptBackground: "/api/images/{image_id}/background/accept",
    userRegister: "/api/users/register",
    userLogin: "/api/users/login"
};

export const boundingBoxColors = [
    "#ff595e", "#ff924c", "#ffca3a", "#c5ca30", "#8ac926", "#52a675", "#1982c4", "#4267ac", "#6a4c93"
]
