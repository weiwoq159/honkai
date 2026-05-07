import { lazy } from "react";
import type { ToolPlugin } from "@plugins/types";

export const fileTypeOrganizerPlugin: ToolPlugin = {
  id: "file-type-organizer",
  name: "按文件类型分类整理",
  description: "按文件扩展名将指定目录下的文件分类移动到对应文件夹中",
  category: "文件处理",
  path: "/tools/file-type-organizer",
  order: 31,
  group: "tools",
  page: lazy(() =>
    import("./pages/FileTypeOrganizerPage").then((module) => ({
      default: module.FileTypeOrganizerPage,
    })),
  ),
};
