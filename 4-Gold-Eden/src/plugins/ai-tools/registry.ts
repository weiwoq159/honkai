import type { FrontendPlugin } from "../types";
import { AiTavernPage } from "./ai_tavern";

export const aiToolsPlugins: FrontendPlugin[] = [
  {
    id: "ai-tavern",
    name: "AI酒馆",
    description: "本地角色卡与 AI 对话工具",
    category: "ai-tools",
    path: "/plugins/ai-tools/ai-tavern",
    order: 100,
    component: AiTavernPage,
  },
];
