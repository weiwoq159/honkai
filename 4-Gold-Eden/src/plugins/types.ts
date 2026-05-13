import type { ComponentType } from "react";

export type PluginCategory =
  | "collector"
  | "automation"
  | "file-tools"
  | "ai-tools";

export interface FrontendPlugin {
  /**
   * 前端插件 ID，要和后端 Python 插件 plugin.json 的 id 保持一致
   * 例如：crawler/pica-comic-crawler
   */
  id: string;

  /**
   * 菜单和页面展示名称
   */
  name: string;

  /**
   * 插件描述，用于 Dashboard、插件卡片、页面说明
   */
  description?: string;

  /**
   * 插件分类
   */
  category: PluginCategory;

  /**
   * 前端路由路径
   * 例如：/plugins/crawler/pica-comic-crawler
   */
  path: string;

  /**
   * 同分类下排序，数字越小越靠前
   */
  order: number;

  /**
   * 插件对应的 React 页面组件
   */
  component: ComponentType;
}

export interface PluginCategoryConfig {
  /**
   * 分类 key
   */
  key: PluginCategory;

  /**
   * 分类名称，用于 Sidebar 展示
   */
  name: string;

  /**
   * 分类排序，数字越小越靠前
   */
  order: number;
}
