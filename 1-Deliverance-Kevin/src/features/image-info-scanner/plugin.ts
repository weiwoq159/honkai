import { lazy } from "react";
import type { ToolPlugin } from "@plugins/types";

export const imageInfoScannerPlugin: ToolPlugin = {
  id: "image-info-scanner",
  name: "图片基础信息扫描",
  description:
    "扫描指定目录下的图片基础信息，包括尺寸、格式、文件大小和修改时间",
  category: "文件处理",
  path: "/tools/image-info-scanner",
  order: 28,
  group: "tools",
  page: lazy(() =>
    import("./pages/ImageInfoScannerPage").then((module) => ({
      default: module.ImageInfoScannerPage,
    })),
  ),
};
