import { Button, Space, Typography } from "antd";
import { ReloadOutlined } from "@ant-design/icons";

const { Text } = Typography;

export function AppHeader() {
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
      <Text strong style={{ fontSize: 16 }}>
        Gold Eden
      </Text>

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
