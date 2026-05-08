import type { FrontendPlugin } from "../types";
import { PicaComicCrawlerPage } from "./PicaComicCrawlerPage";

export const collectorPlugins: FrontendPlugin[] = [
  {
    id: "pica-comic-crawler",
    name: "哔咔漫画采集工具",
    description: "根据漫画地址抓取章节和图片",
    category: "collector",
    path: "/plugins/crawler/pica-comic-crawler",
    order: 100,
    component: PicaComicCrawlerPage,
  },
];
