import {
  AppstoreOutlined,
  HomeOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import { Menu, Typography } from "antd";
import type { MenuProps } from "antd";
import { useLocation, useNavigate } from "react-router-dom";
import { plugins } from "@plugins/registry";

const { Text } = Typography;

type MenuItem = Required<MenuProps>["items"][number];

type PluginGroup = "tools" | "macro" | "spider";

const groupConfig: Record<
  PluginGroup,
  {
    key: string;
    label: string;
    icon: React.ReactNode;
    order: number;
  }
> = {
  spider: {
    key: "spider",
    label: "爬虫",
    icon: <ThunderboltOutlined />,
    order: 20,
  },
  tools: {
    key: "tools",
    label: "工具",
    icon: <AppstoreOutlined />,
    order: 10,
  },
  macro: {
    key: "macro",
    label: "宏",
    icon: <ThunderboltOutlined />,
    order: 20,
  },
};
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type ISafeAny = any;
function getPluginGroup(plugin: (typeof plugins)[number]): PluginGroup {
  return ((plugin as ISafeAny).group || "tools") as PluginGroup;
}

export function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  const groupedPlugins = plugins.reduce<Record<PluginGroup, typeof plugins>>(
    (acc, plugin) => {
      const group = getPluginGroup(plugin);
      if (!acc[group]) {
        acc[group] = [];
      }

      acc[group].push(plugin);

      return acc;
    },
    {
      spider: [],
      tools: [],
      macro: [],
    },
  );

  const pluginGroupItems: MenuItem[] = Object.values(groupConfig)
    .sort((a, b) => a.order - b.order)
    .map((group) => {
      const groupPlugins =
        groupedPlugins[group.key as PluginGroup]?.sort(
          (a, b) => a.order - b.order,
        ) || [];

      if (groupPlugins.length === 0) {
        return null;
      }

      return {
        key: group.key,
        icon: group.icon,
        label: group.label,
        children: groupPlugins.map((plugin) => ({
          key: plugin.path,
          label: plugin.name,
        })),
      };
    })
    .filter(Boolean) as MenuItem[];
  console.log(pluginGroupItems);

  const items: MenuItem[] = [
    {
      key: "/",
      icon: <HomeOutlined />,
      label: "首页",
    },
    ...pluginGroupItems,
  ];

  function handleMenuClick({ key }: { key: string }) {
    if (key === "tools" || key === "yanyun") {
      return;
    }

    navigate(key);
  }

  const defaultOpenKeys = Object.values(groupConfig).map((group) => group.key);

  return (
    <div style={{ height: "100%", padding: 16 }}>
      <div style={{ marginBottom: 24 }}>
        <div
          style={{
            color: "#fff",
            fontSize: 18,
            fontWeight: 700,
            lineHeight: 1.2,
          }}
        >
          Deliverance
        </div>

        <Text style={{ color: "rgba(255,255,255,0.55)", fontSize: 12 }}>
          Local Toolkit
        </Text>
      </div>

      <Menu
        theme="dark"
        mode="inline"
        items={items}
        selectedKeys={[location.pathname]}
        defaultOpenKeys={defaultOpenKeys}
        onClick={handleMenuClick}
        style={{
          borderInlineEnd: "none",
          background: "transparent",
        }}
      />
    </div>
  );
}
