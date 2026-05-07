import { lazy } from "react";
import type { ToolPlugin } from "@plugins/types";

export const folderStatsPlugin: ToolPlugin = {
  id: "folder-stats",
  name: "文件夹详情",
  description: "统计文件夹大小、图片数量、视频数量、创建时间和修改时间",
  category: "文件处理",
  path: "/tools/folder-stats",
  order: 10,
  group: "tools",
  page: lazy(() =>
    import("./pages/FolderStatsPage").then((module) => ({
      default: module.FolderStatsPage,
    })),
  ),
};
