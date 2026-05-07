import { lazy } from "react";
import type { ToolPlugin } from "@plugins/types";

export const duplicateFilenameScannerPlugin: ToolPlugin = {
  id: "duplicate-filename-scanner",
  name: "重复文件名扫描",
  description: "扫描指定目录下的重复文件名，帮助定位不同目录中的同名文件",
  category: "文件处理",
  path: "/tools/duplicate-filename-scanner",
  order: 27,
  group: "tools",
  page: lazy(() =>
    import("./pages/DuplicateFilenameScannerPage").then((module) => ({
      default: module.DuplicateFilenameScannerPage,
    })),
  ),
};
