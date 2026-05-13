import type { FrontendPlugin, PluginCategoryConfig } from "./types";
import { collectorPlugins } from "./collector/registry";
import { automationPlugins } from "./automation/registry";
import { fileToolPlugins } from "./file-tools/registry";
import { aiToolsPlugins } from "./ai-tools/registry";
export const pluginCategories: PluginCategoryConfig[] = [
  {
    key: "ai-tools",
    name: "AI工具",
    order: 100,
  },
  {
    key: "collector",
    name: "采集工具",
    order: 200,
  },
  {
    key: "automation",
    name: "自动化工具",
    order: 300,
  },
  {
    key: "file-tools",
    name: "文件工具",
    order: 400,
  },
];

export const frontendPlugins: FrontendPlugin[] = [
  ...aiToolsPlugins,
  ...collectorPlugins,
  ...automationPlugins,
  ...fileToolPlugins,
];

export function getSortedPlugins(): FrontendPlugin[] {
  return [...frontendPlugins].sort((a, b) => {
    if (a.category !== b.category) {
      const categoryA = pluginCategories.find(
        (category) => category.key === a.category,
      );
      const categoryB = pluginCategories.find(
        (category) => category.key === b.category,
      );

      return (categoryA?.order ?? 999) - (categoryB?.order ?? 999);
    }

    return a.order - b.order;
  });
}

export function getPluginsByCategory(
  category: FrontendPlugin["category"],
): FrontendPlugin[] {
  return getSortedPlugins().filter((plugin) => plugin.category === category);
}

export function getPluginById(pluginId: string): FrontendPlugin | undefined {
  return frontendPlugins.find((plugin) => plugin.id === pluginId);
}

export function getPluginCategoryName(
  categoryKey: FrontendPlugin["category"],
): string {
  const category = pluginCategories.find((item) => item.key === categoryKey);

  return category?.name ?? categoryKey;
}
