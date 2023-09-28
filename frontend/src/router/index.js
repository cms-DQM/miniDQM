import Home from "@/views/HomeView.vue";
import { createRouter, createWebHashHistory } from "vue-router";

const routes = [
  {
    meta: {
      title: "miniDQM",
    },
    path: "/",
    name: "dashboard",
    component: Home,
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 };
  },
});

export default router;
