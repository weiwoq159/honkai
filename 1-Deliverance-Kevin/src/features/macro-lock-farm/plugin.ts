import { lazy } from "react";
import type { ToolPlugin } from "@plugins/types";

export const macroLockFarmPlugin: ToolPlugin = {
  id: "macro-lock-farm",
  name: "宏-刷锁宏",
  description: "燕云十六声刷锁宏，用于执行刷锁相关的本地键鼠自动化流程",
  category: "文件处理",
  path: "/tools/macro-lock-farm",
  order: 46,
  group: "macro",
  page: lazy(() =>
    import("./pages/MacroLockFarmPage").then((module) => ({
      default: module.MacroLockFarmPage,
    })),
  ),
};
