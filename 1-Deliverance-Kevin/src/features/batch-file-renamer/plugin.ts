import { lazy } from "react";
import type { ToolPlugin } from "@plugins/types";

export const batchFileRenamerPlugin: ToolPlugin = {
  id: "batch-file-renamer",
  name: "批量重命名",
  description: "按指定规则批量重命名文件，支持预览和自动处理文件名冲突",
  group: "tools",
  category: "文件处理",
  path: "/tools/batch-file-renamer",
  order: 32,
  page: lazy(() =>
    import("./pages/BatchFileRenamerPage").then((module) => ({
      default: module.BatchFileRenamerPage,
    })),
  ),
};
