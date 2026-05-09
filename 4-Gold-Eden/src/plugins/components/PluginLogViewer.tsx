import { useEffect, useRef } from "react";
import { Empty, Card, Typography } from "antd";

const { Text } = Typography;

interface PluginLogViewerProps {
  logs: string[];
  height?: number;
}

export function PluginLogViewer({ logs, height = 260 }: PluginLogViewerProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = containerRef.current;

    if (!container) {
      return;
    }

    container.scrollTop = container.scrollHeight;
  }, [logs]);

  return (
    <Card title="执行日志">
      {!logs.length ? (
        <div
          style={{
            height,
            border: "1px solid #f0f0f0",
            borderRadius: 8,
            padding: 16,
            background: "#fafafa",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Empty
            description="暂无执行日志"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        </div>
      ) : (
        <div
          ref={containerRef}
          style={{
            height,
            overflowY: "auto",
            border: "1px solid #f0f0f0",
            borderRadius: 8,
            padding: 12,
            background: "#111827",
            fontFamily: "Consolas, Monaco, 'Courier New', monospace",
            fontSize: 12,
            lineHeight: 1.6,
            whiteSpace: "pre-wrap",
          }}
        >
          {logs.map((log, index) => (
            <div key={`${index}-${log.slice(0, 24)}`}>
              <Text style={{ color: "#d1d5db" }}>{log}</Text>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
