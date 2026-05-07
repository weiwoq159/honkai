import { useState } from "react";
import {
  Alert,
  Button,
  Card,
  Divider,
  InputNumber,
  Space,
  Switch,
  Typography,
  message,
} from "antd";
import { PlayCircleOutlined } from "@ant-design/icons";
import { runTool } from "@services/toolRunner";

const { Title, Paragraph, Text } = Typography;

interface RunToolResult {
  success: boolean;
  message: string;
  data?: {
    action?: string;
    logs?: string[];
  };
}

export function MacroPoisonFarmPage() {
  const [loading, setLoading] = useState(false);
  const [loopCount, setLoopCount] = useState<number>(1);
  const [intervalMs, setIntervalMs] = useState<number>(500);
  const [dryRun, setDryRun] = useState<boolean>(false);
  const [activateWindowBeforeRun, setActivateWindowBeforeRun] =
    useState<boolean>(true);
  const [logs, setLogs] = useState<string[]>([]);

  async function handleRun() {
    try {
      setLoading(true);
      setLogs([]);

      const result = (await runTool({
        pluginId: "yanyun-macros",
        input: {
          action: "run_poison_farm",
          config: {
            loopCount,
            intervalMs,
            dryRun,
            activateWindowBeforeRun,
          },
        },
      })) as RunToolResult;

      if (!result.success) {
        message.error(result.message || "刷毒宏执行失败");
        setLogs(result.data?.logs || []);
        return;
      }

      message.success(result.message || "刷毒宏执行完成");
      setLogs(result.data?.logs || []);
    } catch (error) {
      console.error(error);
      message.error(error instanceof Error ? error.message : "刷毒宏执行异常");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 24 }}>
      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <div>
          <Title level={3}>刷毒宏</Title>
          <Paragraph type="secondary">
            燕云十六声刷毒宏，用于执行本地键鼠自动化流程。
          </Paragraph>
        </div>

        <Alert
          type="warning"
          showIcon
          message="使用提醒"
          description="运行前请确认游戏已经启动。建议使用管理员权限运行客户端，避免游戏无法接收键鼠事件。"
        />

        <Card title="运行配置">
          <Space direction="vertical" size={16} style={{ width: "100%" }}>
            <Space wrap size={16}>
              <Space>
                <Text>循环次数</Text>
                <InputNumber
                  min={0}
                  max={999}
                  value={loopCount}
                  onChange={(value) => setLoopCount(value ?? 1)}
                  disabled={loading}
                />
                <Text type="secondary">0 表示无限循环</Text>
              </Space>

              <Space>
                <Text>间隔毫秒</Text>
                <InputNumber
                  min={50}
                  max={10000}
                  step={50}
                  value={intervalMs}
                  onChange={(value) => setIntervalMs(value ?? 500)}
                  disabled={loading}
                />
              </Space>

              <Space>
                <Text>Dry Run</Text>
                <Switch
                  checked={dryRun}
                  onChange={setDryRun}
                  disabled={loading}
                />
              </Space>

              <Space>
                <Text>运行前激活窗口</Text>
                <Switch
                  checked={activateWindowBeforeRun}
                  onChange={setActivateWindowBeforeRun}
                  disabled={loading}
                />
              </Space>
            </Space>

            <Divider style={{ margin: "8px 0" }} />

            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              loading={loading}
              onClick={handleRun}
            >
              启动刷毒宏
            </Button>
          </Space>
        </Card>

        <Card title="执行日志">
          {logs.length === 0 ? (
            <Text type="secondary">暂无日志</Text>
          ) : (
            <pre
              style={{
                margin: 0,
                maxHeight: 360,
                overflow: "auto",
                background: "#111",
                color: "#eee",
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
      </Space>
    </div>
  );
}
