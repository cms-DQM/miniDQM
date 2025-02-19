/**
Author: Ceyhun Uzunoglu <ceyhunuzngl AT gmail [DOT] com>
*/

import { createPinia } from "pinia";
import { createApp } from "vue";

import { darkModeKey, styleKey } from "@/config.js";
import { usePlotsStore } from "@/stores/plots";
import { useStyleStore } from "@/stores/style.js";
import axios from "axios";
import App from "./App.vue";
import router from "./router";

import "./css/main.css";

/* Set axios base url */
const isEnvDev = import.meta.env.DEV;
// console.log("[DEBUG] isEnvDev:" + isEnvDev);
if (isEnvDev) {
  axios.defaults.baseURL = "http://localhost:8081/minidqm/api";
  console.log("[DEBUG] Env:" + isEnvDev);
} else {
  axios.defaults.baseURL = "VITE_BACKEND_API_BASE_URL";
}

/* Init Pinia */
const pinia = createPinia();

/* Create Vue app */
createApp(App).use(router).use(pinia).mount("#app");

/* Init Pinia stores */
const plotsStore = usePlotsStore(pinia);
plotsStore.getAvailableGroups();
plotsStore.getAvailableEras();

const styleStore = useStyleStore(pinia);

/* App style */
styleStore.setStyle(localStorage[styleKey] ?? "basic");

/* Dark mode */
if (
  (!localStorage[darkModeKey] &&
    window.matchMedia("(prefers-color-scheme: dark)").matches) ||
  localStorage[darkModeKey] === "1"
) {
  styleStore.setDarkMode(true);
}

/* Default title tag */
const defaultDocumentTitle = "Home";

/* Set document title from route meta */
router.afterEach((to) => {
  document.title = to.meta?.title
    ? `${to.meta.title} — ${defaultDocumentTitle}`
    : defaultDocumentTitle;
});
