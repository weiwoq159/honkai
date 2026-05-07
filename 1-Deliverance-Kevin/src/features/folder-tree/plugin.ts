import { lazy } from "react";
import type { ToolPlugin } from "@plugins/types";

export const folderTreePlugin: ToolPlugin = {
  id: "folder-tree",
  name: "目录结构查看",
  description: "获取指定文件夹的目录结构",
  category: "文件处理",
  path: "/tools/folder-tree",
  order: 20,
  group: "tools",
  page: lazy(() =>
    import("./pages/FolderTreePage").then((module) => ({
      default: module.FolderTreePage,
    })),
  ),
};
