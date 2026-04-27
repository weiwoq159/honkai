// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/crawler',
  },
  {
    path: '/dashboard',
    name: '主页',
    component: () => import('@apps/Dashboard/Furina-Dashboard.vue'),
  },
  {
    path: '/crawler',
    name: '图片下载',
    component: () => import('@apps/Crawler/ImageCrawler.vue'),
  },
  {
    path: '/folder',
    name: '本地图片',
    redirect: '/ImageFolderBrowser',
    children: [
      {
        name: '图片预览',
        path: '/ImageFolderBrowser',
        component: () => import('@apps/ImageFolderBrowser/ImageFolderBrowser.vue'),
      },
      {
        name: '任务列表',
        path: '/deduplication',
        component: () => import('@apps/ImageFolderBrowser/ImageDeduplication.vue'),
      },
      {
        name: '任务详情',
        path: '/deduplication_detail/:id',
        component: () => import('@apps/ImageFolderBrowser/ImageDeduplicationDetail.vue'),
        props: true, // ✅ 自动将 `id` 注入组件的 props
      },
    ],
  },
  {
    path: '/yan',
    name: '小程序图片',
    component: () => import('@apps/Yan/Yan-Image.vue'),
  },
  // {
  //   path: '/baidu',
  //   name: '一刻相册',
  //   component: () => import('@apps/BaiduPhoto/BaiduPhoto.vue'),
  // },
  {
    path: '/ImageClassifier',
    name: '图片分类',
    component: () => import('@apps/ImageClassifier/ImageClassifier.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
