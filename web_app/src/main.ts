import "./assets/main.css";
import "primevue/resources/themes/aura-dark-blue/theme.css";
import 'primeicons/primeicons.css'

import { createApp } from "vue";
import { createPinia } from "pinia";
import PrimeVue from "primevue/config";
import App from "./App.vue";


const app = createApp(App);

app.use(createPinia()).use(PrimeVue);

app.mount('#app');
