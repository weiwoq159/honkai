import type { LazyExoticComponent, ComponentType } from "react";

export interface ToolPlugin {
  id: string;
  name: string;
  description: string;
  category: string;
  path: string;
  order?: number;
  page: LazyExoticComponent<ComponentType>;
  group: "tools" | "macro" | "spider";
}
