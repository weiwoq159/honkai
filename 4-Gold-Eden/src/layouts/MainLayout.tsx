import type { CSSProperties } from "react";
import { Layout } from "antd";
import { Outlet } from "react-router-dom";
import { AppHeader } from "./components/AppHeader";
import { AppSidebar } from "./components/AppSidebar";
import { AppBreadcrumb } from "./components/AppBreadcrumb";

const { Header, Sider, Content } = Layout;

const layoutStyle: CSSProperties = {
  height: "100vh",
  overflow: "hidden",
};

const headerStyle: CSSProperties = {
  height: 64,
  padding: 0,
  background: "#fff",
  borderBottom: "1px solid #f0f0f0",
  flexShrink: 0,
};

const bodyLayoutStyle: CSSProperties = {
  height: "calc(100vh - 64px)",
  overflow: "hidden",
};

const siderStyle: CSSProperties = {
  background: "#fff",
  borderRight: "1px solid #f0f0f0",
  height: "100%",
  overflow: "auto",
};

const contentStyle: CSSProperties = {
  height: "100%",
  background: "#f5f5f5",
  overflow: "hidden",
  display: "flex",
  flexDirection: "column",
  padding: "0 20px 20px 20px",
};

const breadcrumbWrapperStyle: CSSProperties = {
  padding: "24px 0 0",
  background: "#f5f5f5",
  flexShrink: 0,
};

const pageBodyStyle: CSSProperties = {
  flex: 1,
  overflow: "auto",
  padding: "10px",
  background: "var(--bg, #fff)",
  borderRadius: "8px",
  boxShadow: "0 1px 4px rgba(0, 0, 0, 0.06)",
};

export function MainLayout() {
  return (
    <Layout style={layoutStyle}>
      <Header style={headerStyle}>
        <AppHeader />
      </Header>

      <Layout style={bodyLayoutStyle}>
        <Sider width={240} style={siderStyle}>
          <AppSidebar />
        </Sider>

        <Content style={contentStyle}>
          <div style={breadcrumbWrapperStyle}>
            <AppBreadcrumb />
          </div>

          <div style={pageBodyStyle}>
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  );
}
