import { Card, Typography } from "antd";

const { Text } = Typography;

interface PluginLogViewerProps {
  logs: string[];
}

export function PluginLogViewer({ logs }: PluginLogViewerProps) {
  return (
    <Card title="执行日志">
      {logs.length === 0 ? (
        <Text type="secondary">暂无日志</Text>
      ) : (
        <pre
          style={{
            margin: 0,
            maxHeight: 360,
            overflow: "auto",
            background: "#111827",
            color: "#E5E7EB",
            padding: 12,
            borderRadius: 8,
            fontSize: 13,
            whiteSpace: "pre-wrap",
          }}
        >
          {logs.join("\n")}
        </pre>
      )}
    </Card>
  );
}
