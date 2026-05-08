import { useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Menu, Typography } from "antd";
import {
  AppstoreOutlined,
  CloudDownloadOutlined,
  DashboardOutlined,
  FolderOutlined,
  RobotOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import type { MenuProps } from "antd";
import { getPluginsByCategory, pluginCategories } from "../../plugins/registry";

const { Title } = Typography;

function getCategoryIcon(category: string) {
  if (category === "collector") {
    return <CloudDownloadOutlined />;
  }

  if (category === "automation") {
    return <RobotOutlined />;
  }

  if (category === "file-tools") {
    return <FolderOutlined />;
  }

  return <AppstoreOutlined />;
}

export function AppSidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = useMemo<MenuProps["items"]>(() => {
    return [
      {
        key: "/",
        icon: <DashboardOutlined />,
        label: "Dashboard",
      },
      ...pluginCategories
        .slice()
        .sort((a, b) => a.order - b.order)
        .map((category) => ({
          key: `category-${category.key}`,
          icon: getCategoryIcon(category.key),
          label: category.name,
          children: getPluginsByCategory(category.key).map((plugin) => ({
            key: plugin.path,
            label: plugin.name,
          })),
        })),
      {
        key: "/settings",
        icon: <SettingOutlined />,
        label: "设置",
      },
    ];
  }, []);

  const defaultOpenKeys = useMemo(() => {
    return pluginCategories.map((category) => `category-${category.key}`);
  }, []);

  return (
    <div
      style={{
        height: "100%",
        background: "#fff",
      }}
    >
      <div
        style={{
          height: 64,
          display: "flex",
          alignItems: "center",
          padding: "0 16px",
          borderBottom: "1px solid #f0f0f0",
        }}
      >
        <Title level={4} style={{ margin: 0 }}>
          Gold Eden
        </Title>
      </div>

      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        defaultOpenKeys={defaultOpenKeys}
        items={menuItems}
        style={{
          borderRight: 0,
        }}
        onClick={({ key }) => {
          const target = String(key);

          if (target.startsWith("category-")) {
            return;
          }

          navigate(target);
        }}
      />
    </div>
  );
}
