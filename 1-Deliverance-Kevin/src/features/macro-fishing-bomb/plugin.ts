import { lazy } from "react";
import type { ToolPlugin } from "@plugins/types";

export const macroFishingBombPlugin: ToolPlugin = {
  id: "macro-fishing-bomb",
  name: "炸鱼宏",
  description: "燕云十六声炸鱼宏，用于执行炸鱼相关的本地自动化流程",
  group: "macro",
  category: "游戏宏",
  path: "/yanyun/macro-fishing-bomb",
  order: 1,
  page: lazy(() =>
    import("./pages/MacroFishingBombPage").then((module) => ({
      default: module.MacroFishingBombPage,
    })),
  ),
};
