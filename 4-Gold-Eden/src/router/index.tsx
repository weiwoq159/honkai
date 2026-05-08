import { createBrowserRouter } from "react-router-dom";
import { MainLayout } from "@layouts/MainLayout";
import { DashboardPage } from "../pages/DashboardPage.tsx";
import { SettingsPage } from "../pages/SettingsPage.tsx";
import { NotFoundPage } from "../pages/NotFoundPage.tsx";
import { frontendPlugins } from "../plugins/registry.ts";

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
      ...frontendPlugins.map((plugin) => ({
        path: plugin.path.replace(/^\//, ""),
        element: <plugin.component />,
      })),
      {
        path: "*",
        element: <NotFoundPage />,
      },
    ],
  },
]);
