import { Suspense } from "react";
import { createBrowserRouter } from "react-router-dom";
import { MainLayout } from "../layouts/MainLayout";
import { HomePage } from "../pages/HomePage";
import { plugins } from "@plugins/registry";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },

      ...plugins.map((plugin) => {
        const Page = plugin.page;

        return {
          path: plugin.path.replace(/^\//, ""),
          element: (
            <Suspense fallback={<div>加载中...</div>}>
              <Page />
            </Suspense>
          ),
        };
      }),
    ],
  },
]);
