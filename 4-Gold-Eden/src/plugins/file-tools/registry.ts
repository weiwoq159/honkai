import type { FrontendPlugin } from "../types";
import { BatchFileRenamerPage } from "./BatchFileRenamerPage";

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
];
