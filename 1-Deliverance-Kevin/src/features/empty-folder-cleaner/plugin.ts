import { lazy } from "react";
import type { ToolPlugin } from "@plugins/types";

export const emptyFolderCleanerPlugin: ToolPlugin = {
  id: "empty-folder-cleaner",
  name: "空文件夹清理",
  description: "扫描并清理指定目录下的空文件夹",
  category: "文件处理",
  path: "/tools/empty-folder-cleaner",
  order: 40,
  group: "tools",
  page: lazy(() =>
    import("./pages/EmptyFolderCleanerPage").then((module) => ({
      default: module.EmptyFolderCleanerPage,
    })),
  ),
};
