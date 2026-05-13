import type { FrontendPlugin } from "../types";
import { BatchFileRenamerPage } from "./BatchFileRenamerPage";
import { FolderTreePage } from "./FolderTreePage";
import { FolderFlattenerPage } from "./FolderFlattenerPage";

export const fileToolPlugins: FrontendPlugin[] = [
  {
    id: "batch-file-renamer",
    name: "批量重命名",
    description: "批量修改本地文件名",
    category: "file-tools",
    path: "/plugins/file-tools/batch-file-renamer",
    order: 100,
    component: BatchFileRenamerPage,
  },
  {
    id: "folder-tree",
    name: "目录结构查看",
    description: "获取指定文件夹的目录结构",
    category: "file-tools",
    path: "/plugins/file-tools/folder-tree",
    order: 100,
    component: FolderTreePage,
  },
  {
    id: "folder-flattener",
    name: "拉平文件夹",
    description: "将多层文件夹中的文件提取到目标目录，支持重名处理",
    category: "file-tools",
    path: "/plugins/file-tools/folder-flattener",
    order: 100,
    component: FolderFlattenerPage,
  },
];
