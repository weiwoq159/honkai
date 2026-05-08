import { createBrowserRouter } from "react-router-dom";
import { MainLayout } from "../layouts/MainLayout";
import { DashboardPage } from "../pages/DashboardPage";
import { SettingsPage } from "../pages/SettingsPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { PluginCategoryPage } from "../pages/PluginCategoryPage";
import { frontendPlugins } from "../plugins/registry";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: "settings",
        element: <SettingsPage />,
      },
      {
        path: "plugins/:category",
        element: <PluginCategoryPage />,
      },
      ...frontendPlugins.map((plugin) => {
        const PluginComponent = plugin.component;

        return {
          path: plugin.path.replace(/^\//, ""),
          element: <PluginComponent />,
        };
      }),
      {
        path: "*",
        element: <NotFoundPage />,
      },
    ],
  },
]);
