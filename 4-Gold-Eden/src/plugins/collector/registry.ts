import type { FrontendPlugin } from "../types";
import { PicaComicCrawlerPage } from "./PicaComicCrawlerPage";
import { AliceBookHouseArticleDownloaderPage } from "./AliceBookHouseArticleDownloaderPage";

export const collectorPlugins: FrontendPlugin[] = [
  {
    id: "pica-comic-crawler",
    name: "哔咔漫画采集工具",
    description: "根据漫画地址抓取章节和图片",
    category: "collector",
    path: "/plugins/collector/pica-comic-crawler",
    order: 100,
    component: PicaComicCrawlerPage,
  },
  {
    id: "alice-book-house-article-downloader",
    name: "爱丽丝书屋文章下载",
    description: "根据小说详情页和用户 Cookie 下载爱丽丝书屋文章",
    category: "collector",
    path: "/plugins/collector/alice-book-house-article-downloader",
    order: 100,
    component: AliceBookHouseArticleDownloaderPage,
  },
];
