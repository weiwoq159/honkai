import { lazy } from "react";
import type { ToolPlugin } from "@plugins/types";

export const macroPoisonFarmPlugin: ToolPlugin = {
  id: "macro-poison-farm",
  name: "宏-刷毒宏",
  description: "燕云十六声刷毒宏，用于执行刷毒相关的本地键鼠自动化流程",
  category: "文件处理",
  path: "/tools/macro-poison-farm",
  order: 45,
  group: "macro",
  page: lazy(() =>
    import("./pages/MacroPoisonFarmPage").then((module) => ({
      default: module.MacroPoisonFarmPage,
    })),
  ),
};
