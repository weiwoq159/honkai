import { Breadcrumb, Button, Space, Typography } from "antd";
import { ReloadOutlined } from "@ant-design/icons";
import { useLocation } from "react-router-dom";
import { frontendPlugins, getPluginCategoryName } from "../../plugins/registry";

const { Text } = Typography;

function getPageTitle(pathname: string): string {
  if (pathname === "/") {
    return "Dashboard";
  }

  if (pathname === "/settings") {
    return "设置";
  }

  const plugin = frontendPlugins.find((item) => item.path === pathname);

  if (plugin) {
    return plugin.name;
  }

  return "未知页面";
}

function getBreadcrumbItems(pathname: string) {
  const plugin = frontendPlugins.find((item) => item.path === pathname);

  if (pathname === "/") {
    return [
      {
        title: "Dashboard",
      },
    ];
  }

  if (pathname === "/settings") {
    return [
      {
        title: "首页",
      },
      {
        title: "设置",
      },
    ];
  }

  if (plugin) {
    return [
      {
        title: "首页",
      },
      {
        title: getPluginCategoryName(plugin.category),
      },
      {
        title: plugin.name,
      },
    ];
  }

  return [
    {
      title: "首页",
    },
    {
      title: "未知页面",
    },
  ];
}

export function AppHeader() {
  const location = useLocation();

  const title = getPageTitle(location.pathname);
  const breadcrumbItems = getBreadcrumbItems(location.pathname);

  return (
    <div
      style={{
        height: 64,
        padding: "0 24px",
        background: "#fff",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
      }}
    >
      <Space direction="vertical" size={2}>
        <Text strong style={{ fontSize: 16 }}>
          {title}
        </Text>

        <Breadcrumb items={breadcrumbItems} />
      </Space>

      <Space>
        <Button
          icon={<ReloadOutlined />}
          onClick={() => {
            window.location.reload();
          }}
        >
          刷新
        </Button>
      </Space>
    </div>
  );
}
