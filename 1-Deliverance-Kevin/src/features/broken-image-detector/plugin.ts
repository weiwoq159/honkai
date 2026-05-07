import { lazy } from "react";
import type { ToolPlugin } from "@plugins/types";

export const brokenImageDetectorPlugin: ToolPlugin = {
  id: "broken-image-detector",
  name: "图片损坏检测",
  description: "扫描指定目录下无法正常读取或解码的损坏图片文件",
  category: "文件处理",
  path: "/tools/broken-image-detector",
  order: 29,
  group: "tools",
  page: lazy(() =>
    import("./pages/BrokenImageDetectorPage").then((module) => ({
      default: module.BrokenImageDetectorPage,
    })),
  ),
};
