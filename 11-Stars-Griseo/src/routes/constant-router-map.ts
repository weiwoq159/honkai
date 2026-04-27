import type { RouteRecordRaw } from "vue-router";

const routes: Array<RouteRecordRaw> = [
  { path: "/", name: "总览", redirect: "/dashboard" },
  {
    path: "/dashboard",
    name: "dashboard",
    component: () => import("@views/Dashboard/Dashboard.vue"),
    children: [],
  },
  {
    path: "/albums",
    name: "albums",
    component: () => import("@views/Albums/AlbumsList.vue"),
    children: [],
  },
  {
    path: "/crawler",
    name: "crawler",
    component: () => import("@views/Crawler/crawler.vue"),
    children: [],
  },
  // { path: '/crawler', name: 'crawler', component: () => import('@renderer/views/crawler/Crawler.vue')}
];

export default routes;
