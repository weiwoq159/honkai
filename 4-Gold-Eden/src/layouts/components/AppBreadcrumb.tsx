import { Breadcrumb, Typography } from "antd";
import { Link, useLocation } from "react-router-dom";
import { frontendPlugins, getPluginCategoryName } from "../../plugins/registry";
import type { PluginCategory } from "../../plugins/types";

const { Title } = Typography;

function getPageTitle(pathname: string): string {
  if (pathname === "/") {
    return "Dashboard";
  }

  if (pathname === "/settings") {
    return "设置";
  }

  const categoryMatch = pathname.match(/^\/plugins\/([^/]+)$/);

  if (categoryMatch) {
    return getPluginCategoryName(categoryMatch[1] as PluginCategory);
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
        title: <Link to="/">首页</Link>,
      },
      {
        title: "Dashboard",
      },
    ];
  }

  if (pathname === "/settings") {
    return [
      {
        title: <Link to="/">首页</Link>,
      },
      {
        title: "设置",
      },
    ];
  }

  const categoryMatch = pathname.match(/^\/plugins\/([^/]+)$/);

  if (categoryMatch) {
    const categoryKey = categoryMatch[1] as PluginCategory;

    return [
      {
        title: <Link to="/">首页</Link>,
      },
      {
        title: getPluginCategoryName(categoryKey),
      },
    ];
  }

  if (plugin) {
    const categoryPath = `/plugins/${plugin.category}`;

    return [
      {
        title: <Link to="/">首页</Link>,
      },
      {
        title: (
          <Link to={categoryPath}>
            {getPluginCategoryName(plugin.category)}
          </Link>
        ),
      },
      {
        title: plugin.name,
      },
    ];
  }

  return [
    {
      title: <Link to="/">首页</Link>,
    },
    {
      title: "未知页面",
    },
  ];
}

export function AppBreadcrumb() {
  const location = useLocation();

  const title = getPageTitle(location.pathname);
  const breadcrumbItems = getBreadcrumbItems(location.pathname);

  return (
    <div
      style={{
        marginBottom: 16,
      }}
    >
      <Title level={4} style={{ margin: "0 0 8px" }}>
        {title}
      </Title>

      <Breadcrumb items={breadcrumbItems} />
    </div>
  );
}
