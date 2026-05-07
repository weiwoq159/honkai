import { lazy } from "react";
import type { ToolPlugin } from "@plugins/types";

export const duplicateImageScannerPlugin: ToolPlugin = {
  id: "duplicate-image-scanner",
  name: "图片重复扫描",
  description: "扫描指定目录下的相似或重复图片，并按相似度分组展示",
  category: "文件处理",
  path: "/tools/duplicate-image-scanner",
  order: 33,
  group: "tools",
  page: lazy(() =>
    import("./pages/DuplicateImageScannerPage").then((module) => ({
      default: module.DuplicateImageScannerPage,
    })),
  ),
};
