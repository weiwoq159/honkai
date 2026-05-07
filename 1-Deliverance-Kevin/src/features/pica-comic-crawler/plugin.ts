import { lazy } from "react";
import type { ToolPlugin } from "@plugins/types";

export const picaComicCrawlerPlugin: ToolPlugin = {
  id: "pica-comic-crawler",
  name: "哔咔漫画爬取",
  description: "根据章节分页接口下载漫画图片",
  category: "爬虫",
  path: "/tools/pica-comic-crawler",
  order: 80,
  group: "spider",
  page: lazy(() =>
    import("./pages/PicaComicCrawlerPage").then((module) => ({
      default: module.PicaComicCrawlerPage,
    })),
  ),
};
