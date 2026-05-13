import { useEffect, useMemo, useRef, useState } from "react";
import {
  Button,
  Card,
  InputNumber,
  Space,
  Switch,
  Typography,
  message,
  Alert,
  Divider,
  Progress,
  Tag,
  List,
} from "antd";
import { PlayCircleOutlined, StopOutlined } from "@ant-design/icons";
import { listen, type UnlistenFn } from "@tauri-apps/api/event";
import { runTool } from "@services/toolRunner";

const { Title, Paragraph, Text } = Typography;

type YanyunLockMacroInput = {
  loopCount: number;
  intervalMs: number;
  enableSafetyDelay: boolean;
  debug: boolean;
};

type YanyunLockMacroData = {
  totalCount?: number;
  successCount?: number;
  failedCount?: number;
  logs?: string[];
};

type ToolProgressPayload = {
  pluginId: string;
  data: MacroProgressData;
};

type ToolLogPayload = {
  pluginId: string;
  data: string;
};

type MacroProgressData = {
  stage?: "started" | "running" | "completed" | "error" | string;
  percent?: number;
  message?: string;
  current?: number;
  total?: number | null;

  macroId?: string;
  macroName?: string;
  round?: number;
  executedCount?: number;
  loopCount?: number;
  isInfinite?: boolean;
  error?: string;
};

const PLUGIN_ID = "yanyun-lock-macro";

export function YanyunLockMacroPage() {
  const [loading, setLoading] = useState(false);

  const [loopCount, setLoopCount] = useState<number>(0);
  const [intervalMs, setIntervalMs] = useState<number>(10000);
  const [enableSafetyDelay, setEnableSafetyDelay] = useState(true);
  const [debug, setDebug] = useState(true);

  const [progress, setProgress] = useState<MacroProgressData | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [finalResult, setFinalResult] = useState<YanyunLockMacroData | null>(
    null
  );

  const logsEndRef = useRef<HTMLDivElement | null>(null);

  const isInfinite = useMemo(() => {
    if (!progress) return loopCount === 0;

    return (
      progress.isInfinite === true ||
      progress.loopCount === 0 ||
      progress.total === null ||
      loopCount === 0
    );
  }, [progress, loopCount]);

  const executedCount = progress?.executedCount ?? progress?.round ?? 0;

  const percent = useMemo(() => {
    if (!progress) return 0;
    if (isInfinite) return 100;

    const value = Number(progress.percent ?? 0);
    return Math.max(0, Math.min(100, value));
  }, [progress, isInfinite]);

  const progressStatus = useMemo(() => {
    if (progress?.stage === "error") return "exception";
    if (progress?.stage === "completed") return "success";
    if (loading) return "active";

    return "normal";
  }, [progress?.stage, loading]);

  const stageText = useMemo(() => {
    switch (progress?.stage) {
      case "started":
        return "已启动";
      case "running":
        return "运行中";
      case "completed":
        return "已完成";
      case "error":
        return "执行失败";
      default:
        return loading ? "运行中" : "未启动";
    }
  }, [progress?.stage, loading]);

  useEffect(() => {
    let unlistenProgress: UnlistenFn | null = null;
    let unlistenLog: UnlistenFn | null = null;

    const setupListeners = async () => {
      unlistenProgress = await listen<ToolProgressPayload>(
        "tool-progress",
        (event) => {
          const payload = event.payload;

          if (payload.pluginId !== PLUGIN_ID) {
            return;
          }

          setProgress(payload.data);

          if (payload.data?.message) {
            setLogs((prev) => [...prev, payload.data.message as string]);
          }
        }
      );

      unlistenLog = await listen<ToolLogPayload>("tool-log", (event) => {
        const payload = event.payload;

        if (payload.pluginId !== PLUGIN_ID) {
          return;
        }

        if (!payload.data) {
          return;
        }

        setLogs((prev) => [...prev, payload.data]);
      });
    };

    setupListeners();

    return () => {
      unlistenProgress?.();
      unlistenLog?.();
    };
  }, []);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const resetRuntimeState = () => {
    setProgress(null);
    setLogs([]);
    setFinalResult(null);
  };

  const handleRun = async () => {
    const input: YanyunLockMacroInput = {
      loopCount,
      intervalMs,
      enableSafetyDelay,
      debug,
    };

    try {
      resetRuntimeState();
      setLoading(true);

      setLogs((prev) => [
        ...prev,
        `准备启动刷锁宏，循环次数：${
          loopCount === 0 ? "无限循环" : `${loopCount} 次`
        }，单轮间隔：${intervalMs}ms`,
      ]);

      const result = await runTool<YanyunLockMacroData, YanyunLockMacroInput>({
        pluginId: PLUGIN_ID,
        input,
      });

      setFinalResult(result.data ?? null);

      if (result.data?.logs?.length) {
        setLogs((prev) => [...prev, ...result.data!.logs!]);
      }

      if (result.success) {
        message.success(result.message || "刷锁宏执行完成");

        if (!progress || progress.stage !== "completed") {
          setProgress((prev) => ({
            ...prev,
            stage: "completed",
            percent: 100,
            message: result.message || "刷锁宏执行完成",
            executedCount:
              prev?.executedCount ??
              prev?.round ??
              result.data?.successCount ??
              result.data?.totalCount ??
              0,
            loopCount,
            isInfinite: loopCount === 0,
          }));
        }
      } else {
        message.error(result.message || "刷锁宏执行失败");

        setProgress((prev) => ({
          ...prev,
          stage: "error",
          message: result.message || "刷锁宏执行失败",
          loopCount,
          isInfinite: loopCount === 0,
        }));
      }
    } catch (error) {
      console.error(error);

      const errorMessage =
        error instanceof Error ? error.message : "刷锁宏执行异常，请查看控制台或日志";

      setProgress((prev) => ({
        ...prev,
        stage: "error",
        message: errorMessage,
        loopCount,
        isInfinite: loopCount === 0,
      }));

      setLogs((prev) => [...prev, errorMessage]);
      message.error("刷锁宏执行异常，请查看控制台或日志");
    } finally {
      setLoading(false);
    }
  };

  const handleStop = () => {
    message.info("当前页面仅提供启动参数配置，停止逻辑需要后端插件支持");
  };

  return (
    <div style={{ padding: 24 }}>
      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <Card>
          <Title level={3} style={{ marginTop: 0 }}>
            刷锁宏
          </Title>

          <Paragraph type="secondary">
            用于自动执行燕云十六声刷锁相关操作。启动前请确认游戏窗口已打开，
            并且当前画面处于宏可以识别和操作的状态。
          </Paragraph>

          <Alert
            type="warning"
            showIcon
            message="使用前提醒"
            description="宏执行过程中会模拟键盘或鼠标操作，请不要切换窗口、移动鼠标或手动操作游戏窗口。"
          />
        </Card>

        <Card title="运行参数">
          <Space direction="vertical" size={20} style={{ width: "100%" }}>
            <div>
              <Text strong>循环次数</Text>
              <Paragraph type="secondary" style={{ marginBottom: 8 }}>
                设置宏执行次数。设置为 0 表示无限循环，设置为 1 表示只执行一轮。
              </Paragraph>

              <InputNumber
                min={0}
                value={loopCount}
                disabled={loading}
                onChange={(value) => setLoopCount(value ?? 0)}
                style={{ width: 240 }}
                addonAfter="次"
              />
            </div>

            <div>
              <Text strong>单轮间隔</Text>
              <Paragraph type="secondary" style={{ marginBottom: 8 }}>
                每轮执行完成后的等待时间。建议保持在 10 秒左右，避免操作过快。
              </Paragraph>

              <InputNumber
                min={1000}
                step={1000}
                value={intervalMs}
                disabled={loading}
                onChange={(value) => setIntervalMs(value ?? 10000)}
                style={{ width: 240 }}
                addonAfter="ms"
              />
            </div>

            <div>
              <Space>
                <Switch
                  checked={enableSafetyDelay}
                  disabled={loading}
                  onChange={setEnableSafetyDelay}
                />
                <Text strong>启用安全延迟</Text>
              </Space>

              <Paragraph type="secondary" style={{ marginTop: 8 }}>
                开启后会在关键操作之间增加等待时间，提高稳定性。
              </Paragraph>
            </div>

            <div>
              <Space>
                <Switch checked={debug} disabled={loading} onChange={setDebug} />
                <Text strong>输出调试日志</Text>
              </Space>

              <Paragraph type="secondary" style={{ marginTop: 8 }}>
                开启后会输出识别结果、操作步骤和异常信息，方便排查问题。
              </Paragraph>
            </div>
          </Space>
        </Card>

        <Card title="运行状态">
          <Space direction="vertical" size={12} style={{ width: "100%" }}>
            <Space wrap>
              <Tag color={loading ? "processing" : undefined}>{stageText}</Tag>

              {isInfinite ? (
                <Tag color="blue">无限循环</Tag>
              ) : (
                <Tag color="blue">有限循环</Tag>
              )}

              <Text type="secondary">
                {isInfinite
                  ? `已执行 ${executedCount} 次`
                  : `已执行 ${progress?.current ?? executedCount} / ${
                      progress?.total ?? loopCount
                    } 次`}
              </Text>
            </Space>

            {isInfinite ? (
              <>
                <Progress
                  percent={100}
                  status={progressStatus}
                  showInfo={false}
                />
                <Text type="secondary">
                  无限循环模式不计算总百分比，仅展示运行状态和已执行次数。
                </Text>
              </>
            ) : (
              <Progress percent={percent} status={progressStatus} />
            )}

            {progress?.message ? (
              <Alert
                type={progress.stage === "error" ? "error" : "info"}
                showIcon
                message={progress.message}
              />
            ) : (
              <Alert
                type="info"
                showIcon
                message="尚未收到宏执行进度"
                description="启动后，Python 会通过 stderr 输出进度事件，Rust 会转发到前端。"
              />
            )}

            {finalResult ? (
              <div>
                <Divider style={{ margin: "12px 0" }} />
                <Space wrap>
                  <Text type="secondary">最终结果：</Text>
                  <Tag>总数：{finalResult.totalCount ?? "-"}</Tag>
                  <Tag color="success">成功：{finalResult.successCount ?? "-"}</Tag>
                  <Tag color="error">失败：{finalResult.failedCount ?? "-"}</Tag>
                </Space>
              </div>
            ) : null}
          </Space>
        </Card>

        <Card title="实时日志">
          {logs.length === 0 ? (
            <Text type="secondary">暂无日志</Text>
          ) : (
            <div
              style={{
                maxHeight: 260,
                overflow: "auto",
                border: "1px solid #f0f0f0",
                borderRadius: 8,
                padding: 12,
                background: "#fafafa",
              }}
            >
              <List
                size="small"
                dataSource={logs}
                renderItem={(item, index) => (
                  <List.Item style={{ padding: "4px 0" }}>
                    <Text type="secondary" style={{ marginRight: 8 }}>
                      #{index + 1}
                    </Text>
                    <Text>{item}</Text>
                  </List.Item>
                )}
              />
              <div ref={logsEndRef} />
            </div>
          )}
        </Card>

        <Card title="操作">
          <Space>
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              loading={loading}
              disabled={loading}
              onClick={handleRun}
            >
              启动刷锁宏
            </Button>

            <Button danger icon={<StopOutlined />} onClick={handleStop}>
              停止宏
            </Button>
          </Space>

          <Divider />

          <Paragraph type="secondary" style={{ marginBottom: 0 }}>
            如果点击启动后无反应，优先检查：插件 ID 是否为{" "}
            <Text code>{PLUGIN_ID}</Text>，后端 Python 插件是否存在，Rust
            命令是否已注册。
          </Paragraph>
        </Card>
      </Space>
    </div>
  );
}