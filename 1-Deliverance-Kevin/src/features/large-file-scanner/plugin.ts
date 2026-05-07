import { lazy } from "react";
import type { ToolPlugin } from "@plugins/types";

export const largeFileScannerPlugin: ToolPlugin = {
  id: "large-file-scanner",
  name: "大文件扫描",
  description: "扫描指定目录下的大文件，帮助定位占用空间较大的文件",
  category: "文件处理",
  path: "/tools/large-file-scanner",
  order: 50,
  group: "tools",
  page: lazy(() =>
    import("./pages/LargeFileScannerPage").then((module) => ({
      default: module.LargeFileScannerPage,
    })),
  ),
};
