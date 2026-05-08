import { Layout } from "antd";
import { Outlet } from "react-router-dom";
import { AppHeader } from "./components/AppHeader";
import { AppSidebar } from "./components/AppSidebar";

const { Header, Sider, Content } = Layout;

const layoutStyle: React.CSSProperties = {
  minHeight: "100vh",
};

const headerStyle: React.CSSProperties = {
  height: 64,
  padding: 0,
  background: "#fff",
  borderBottom: "1px solid #f0f0f0",
};

const siderStyle: React.CSSProperties = {
  background: "#fff",
  borderRight: "1px solid #f0f0f0",
};

const contentStyle: React.CSSProperties = {
  padding: 24,
  background: "#f5f5f5",
  minHeight: "calc(100vh - 64px)",
  overflow: "auto",
};

export function MainLayout() {
  return (
    <Layout style={layoutStyle}>
      <Header style={headerStyle}>
        <AppHeader />
      </Header>

      <Layout>
        <Sider width={240} style={siderStyle}>
          <AppSidebar />
        </Sider>

        <Content style={contentStyle}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
