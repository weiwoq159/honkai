import type { FrontendPlugin } from "../types";
import { YanyunLockMacroPage } from "./YanyunLockMacroPage";

export const automationPlugins: FrontendPlugin[] = [
  {
    id: "yanyun-lock-macro",
    name: "刷锁宏",
    description: "燕云十六声刷锁自动化宏",
    category: "automation",
    path: "/plugins/automation/yanyun-lock-macro",
    order: 100,
    component: YanyunLockMacroPage,
  },
];
