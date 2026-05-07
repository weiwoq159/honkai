import { Layout } from "antd";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
const { Header, Sider, Content } = Layout;

const layoutStyle: React.CSSProperties = {
  height: "100vh",
};

const siderStyle: React.CSSProperties = {
  background: "#111827",
  color: "#fff",
};

const headerStyle: React.CSSProperties = {
  height: 64,
  padding: "0 24px",
  background: "#fff",
  borderBottom: "1px solid #e5e7eb",
};

const contentStyle: React.CSSProperties = {
  padding: 24,
  overflow: "auto",
  background: "#f3f4f6",
};

export function MainLayout() {
  return (
    <Layout style={layoutStyle}>
      <Sider width={260} style={siderStyle}>
        <Sidebar />
      </Sider>

      <Layout>
        <Header style={headerStyle}>Header</Header>
        <Content style={contentStyle}>
          <Outlet></Outlet>
        </Content>
      </Layout>
    </Layout>
  );
}
