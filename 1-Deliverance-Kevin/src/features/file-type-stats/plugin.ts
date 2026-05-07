import { lazy } from "react";
import type { ToolPlugin } from "@plugins/types";

export const fileTypeStatsPlugin: ToolPlugin = {
  id: "file-type-stats",
  name: "文件类型统计",
  description:
    "扫描指定目录下的文件类型分布，统计不同扩展名的文件数量和占用空间",
  category: "文件处理",
  path: "/tools/file-type-stats",
  order: 26,
  group: "tools",
  page: lazy(() =>
    import("./pages/FileTypeStatsPage").then((module) => ({
      default: module.FileTypeStatsPage,
    })),
  ),
};
