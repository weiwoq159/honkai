import { lazy } from "react";
import type { ToolPlugin } from "@plugins/types";

export const folderFlattenPlugin: ToolPlugin = {
  id: "folder-flatten",
  name: "文件夹拉平",
  description: "将多层文件夹中的文件整理到同一层级",
  category: "文件处理",
  path: "/tools/folder-flatten",
  order: 30,
  group: "tools",
  page: lazy(() =>
    import("./pages/FolderFlattenPage").then((module) => ({
      default: module.FolderFlattenPage,
    })),
  ),
};
