/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Descriptions,
  Form,
  Input,
  InputNumber,
  Progress,
  Space,
  Switch,
  Typography,
  message,
} from "antd";
import {
  CloudDownloadOutlined,
  FolderOpenOutlined,
  LinkOutlined,
} from "@ant-design/icons";
import { open } from "@tauri-apps/plugin-dialog";
import { revealItemInDir } from "@tauri-apps/plugin-opener";

import { PluginLogViewer } from "../components/PluginLogViewer";
import {
  listenToolLog,
  listenToolProgress,
  runTool,
} from "../../services/toolRunner";

const { Text } = Typography;

interface FailedChapterItem {
  index?: string;
  title?: string;
  url?: string;
  error?: string;
}

interface AliceBookHouseDownloaderData {
  action?: string;
  pluginId?: string;

  detailUrl?: string;
  novelId?: string;
  novelTitle?: string;
  novelDetailUrl?: string;
  chapterListUrl?: string;

  outputDir?: string;
  txtPath?: string;
  progressPath?: string;

  chapterCount?: number;
  selectedChapterCount?: number;
  successCount?: number;
  skippedCount?: number;
  failedCount?: number;

  startIndex?: number;
  endIndex?: number | null;
  nextStartIndex?: number;

  stoppedByRateLimit?: boolean;
  failedChapters?: FailedChapterItem[];

  logs?: string[];
}

interface AliceBookHouseDownloaderFormValues {
  detailUrl: string;
  cookie: string;
  outputDir: string;

  startIndex?: number;
  endIndex?: number;
  chapterSleepMin?: number;
  chapterSleepMax?: number;
  restart?: boolean;
}

interface AliceBookHouseDownloaderProgress {
  stage:
    | "preparing"
    | "fetching_detail"
    | "parsing_chapters"
    | "downloading"
    | "completed"
    | "error";
  percent: number;
  current?: number;
  total?: number;
  chapterTitle?: string;
  message?: string;
}

function getProgressStatus(
  loading: boolean,
  progress: AliceBookHouseDownloaderProgress | null,
): "normal" | "active" | "success" | "exception" {
  if (progress?.stage === "error") {
    return "exception";
  }

  if (progress?.stage === "completed") {
    return "success";
  }

  if (loading) {
    return "active";
  }

  return "normal";
}

function normalizeOptionalText(value?: string): string {
  return String(value || "").trim();
}

function normalizeOptionalNumber(value?: number | null): number | undefined {
  if (value === null || value === undefined) {
    return undefined;
  }

  if (Number.isNaN(Number(value))) {
    return undefined;
  }

  return Number(value);
}

export function AliceBookHouseArticleDownloaderPage() {
  const [form] = Form.useForm<AliceBookHouseDownloaderFormValues>();

  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [resultData, setResultData] =
    useState<AliceBookHouseDownloaderData | null>(null);
  const [progress, setProgress] =
    useState<AliceBookHouseDownloaderProgress | null>(null);

  useEffect(() => {
    form.setFieldsValue({
      startIndex: 1,
      endIndex: 20,
      chapterSleepMin: 8,
      chapterSleepMax: 12,
      restart: false,
    });
  }, [form]);

  useEffect(() => {
    const unlistenList: Array<() => void> = [];

    listenToolProgress<AliceBookHouseDownloaderProgress>((payload) => {
      if (payload.pluginId !== "alice-book-house-article-downloader") {
        return;
      }

      setProgress(payload.data);
    }).then((unlisten) => {
      unlistenList.push(unlisten);
    });

    listenToolLog<string>((payload) => {
      if (payload.pluginId !== "alice-book-house-article-downloader") {
        return;
      }

      setLogs((prevLogs) => [...prevLogs, String(payload.data)]);
    }).then((unlisten) => {
      unlistenList.push(unlisten);
    });

    return () => {
      unlistenList.forEach((unlisten) => unlisten());
    };
  }, []);

  async function handleSelectOutputDir() {
    try {
      const selected = await open({
        directory: true,
        multiple: false,
        title: "选择文章保存文件夹",
      });

      if (!selected) {
        return;
      }

      const outputDir = Array.isArray(selected) ? selected[0] : selected;

      if (!outputDir) {
        return;
      }

      form.setFieldsValue({
        outputDir,
      });

      await form.validateFields(["outputDir"]);
    } catch (error) {
      console.error(error);
      message.error("选择文件夹失败");
    }
  }

  async function handleRun(values: AliceBookHouseDownloaderFormValues) {
    try {
      setLoading(true);
      setLogs([]);
      setResultData(null);
      setProgress({
        stage: "preparing",
        percent: 0,
        message: "准备开始下载任务",
      });

      const detailUrl = normalizeOptionalText(values.detailUrl);
      const cookie = normalizeOptionalText(values.cookie);
      const outputDir = normalizeOptionalText(values.outputDir);

      const startIndex = normalizeOptionalNumber(values.startIndex) || 1;
      const endIndex = normalizeOptionalNumber(values.endIndex);
      const chapterSleepMin =
        normalizeOptionalNumber(values.chapterSleepMin) ?? 8;
      const chapterSleepMax =
        normalizeOptionalNumber(values.chapterSleepMax) ?? 12;
      const restart = Boolean(values.restart);

      const result = await runTool({
        pluginId: "alice-book-house-article-downloader",
        input: {
          action: "run",
          config: {
            detailUrl,
            cookie,
            outputDir,
            startIndex,
            ...(endIndex ? { endIndex } : {}),
            chapterSleepMin,
            chapterSleepMax,
            restart,
          },
        },
      });

      console.log("alice book house downloader result:", result);

      const rawData = result.data as any;

      const normalizedData: AliceBookHouseDownloaderData | null =
        rawData?.data && typeof rawData.data === "object"
          ? rawData.data
          : rawData || null;

      const resultLogs =
        result.logs || normalizedData?.logs || rawData?.logs || [];

      if (resultLogs.length > 0) {
        setLogs(resultLogs);
      }

      setResultData(normalizedData);

      if (result.success) {
        setProgress((prevProgress) => ({
          stage: normalizedData?.stoppedByRateLimit ? "error" : "completed",
          percent: normalizedData?.stoppedByRateLimit
            ? prevProgress?.percent || 0
            : 100,
          current: prevProgress?.total,
          total: prevProgress?.total,
          message: normalizedData?.stoppedByRateLimit
            ? "检测到访问限制，任务已停止"
            : "下载任务执行完成",
        }));

        if (normalizedData?.stoppedByRateLimit) {
          message.warning(
            `检测到访问限制，建议下次从第 ${
              normalizedData.nextStartIndex || startIndex
            } 章继续`,
          );
        } else {
          message.success(result.message || "下载任务执行完成");
        }
      } else {
        setProgress((prevProgress) => ({
          stage: "error",
          percent: prevProgress?.percent || 0,
          message: result.message || "下载任务执行失败",
        }));

        message.error(result.message || "下载任务执行失败");
      }
    } catch (error) {
      console.error(error);

      const errorMessage =
        error instanceof Error
          ? error.message
          : typeof error === "string"
            ? error
            : "下载任务执行异常";

      setProgress((prevProgress) => ({
        stage: "error",
        percent: prevProgress?.percent || 0,
        message: errorMessage,
      }));

      message.error(errorMessage);
      setLogs((prevLogs) => [...prevLogs, `[ERROR] ${errorMessage}`]);
    } finally {
      setLoading(false);
    }
  }

  async function handleRevealPath(path?: string) {
    if (!path) {
      message.warning("暂无路径");
      return;
    }

    try {
      await revealItemInDir(path);
    } catch (error) {
      console.error(error);
      message.error("打开路径失败");
    }
  }

  function handleUseNextStartIndex() {
    if (!resultData?.nextStartIndex) {
      message.warning("暂无下一次起始章节");
      return;
    }

    form.setFieldsValue({
      startIndex: resultData.nextStartIndex,
    });

    message.success(`已设置起始章节为 ${resultData.nextStartIndex}`);
  }

  function handleReset() {
    form.resetFields();

    form.setFieldsValue({
      startIndex: 1,
      endIndex: 20,
      chapterSleepMin: 8,
      chapterSleepMax: 12,
      restart: false,
    });

    setLogs([]);
    setResultData(null);
    setProgress(null);
  }

  const progressPercent = progress?.percent ?? 0;
  const progressStatus = getProgressStatus(loading, progress);

  return (
    <Space direction="vertical" size={16} style={{ width: "100%" }}>
      <Alert
        type="warning"
        showIcon
        message="爱丽丝书屋文章下载"
        description="支持断点续传。默认不会删除已有 TXT 和进度文件；只有开启“重新下载”时，才会删除旧 TXT 和旧 progress。Cookie 属于敏感信息，不会展示在执行结果中。"
      />

      <Card title="下载配置">
        <Form<AliceBookHouseDownloaderFormValues>
          form={form}
          layout="vertical"
          onFinish={handleRun}
          disabled={loading}
        >
          <Form.Item
            label="小说详情页"
            name="detailUrl"
            rules={[
              { required: true, message: "请输入小说详情页地址" },
              {
                validator: (_, value) => {
                  if (!value) {
                    return Promise.resolve();
                  }

                  const text = String(value).trim();

                  if (
                    text.startsWith("http://") ||
                    text.startsWith("https://") ||
                    /^\d+$/.test(text)
                  ) {
                    return Promise.resolve();
                  }

                  return Promise.reject(
                    new Error("请输入有效的小说详情页地址或小说 ID"),
                  );
                },
              },
            ]}
          >
            <Input
              prefix={<LinkOutlined />}
              placeholder="例如：https://www.alicesw.com/novel/30108.html"
              allowClear
              disabled={loading}
            />
          </Form.Item>

          <Form.Item
            label="用户 Cookie"
            name="cookie"
            rules={[{ required: true, message: "请输入用户 Cookie" }]}
            extra="敏感信息。只用于请求爱丽丝书屋页面，不会写入执行结果。"
          >
            <Input.TextArea
              placeholder="例如：key1=value1; key2=value2"
              rows={4}
              allowClear
              disabled={loading}
            />
          </Form.Item>

          <Form.Item label="保存地址" required>
            <Space.Compact style={{ width: "100%" }}>
              <Form.Item
                name="outputDir"
                noStyle
                rules={[{ required: true, message: "请选择文章保存文件夹" }]}
              >
                <Input
                  prefix={<FolderOpenOutlined />}
                  placeholder="请选择文章保存文件夹"
                  allowClear
                  readOnly
                  disabled={loading}
                />
              </Form.Item>

              <Button disabled={loading} onClick={handleSelectOutputDir}>
                选择文件夹
              </Button>
            </Space.Compact>
          </Form.Item>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "120px 120px 120px 120px 240px",
              columnGap: 24,
              alignItems: "start",
              width: "100%",
              marginBottom: 24,
            }}
          >
            <Form.Item
              label="起始章节"
              name="startIndex"
              required
              style={{ marginBottom: 0 }}
            >
              <InputNumber min={1} style={{ width: "100%" }} />
            </Form.Item>

            <Form.Item
              label="结束章节"
              name="endIndex"
              extra="不填则下载到最后"
              style={{ marginBottom: 0 }}
            >
              <InputNumber min={1} style={{ width: "100%" }} />
            </Form.Item>

            <Form.Item
              label="最小间隔 / 秒"
              name="chapterSleepMin"
              required
              style={{ marginBottom: 0 }}
            >
              <InputNumber min={1} style={{ width: "100%" }} />
            </Form.Item>

            <Form.Item
              label="最大间隔 / 秒"
              name="chapterSleepMax"
              required
              style={{ marginBottom: 0 }}
            >
              <InputNumber min={1} style={{ width: "100%" }} />
            </Form.Item>

            <Form.Item
              label="重新下载"
              name="restart"
              valuePropName="checked"
              extra="开启后会删除旧 TXT 和旧进度"
              style={{ marginBottom: 0 }}
            >
              <Switch />
            </Form.Item>
          </div>

          <Space>
            <Button
              type="primary"
              htmlType="submit"
              icon={<CloudDownloadOutlined />}
              loading={loading}
            >
              开始下载
            </Button>

            <Button
              disabled={loading || !resultData?.nextStartIndex}
              onClick={handleUseNextStartIndex}
            >
              从下一章继续
            </Button>

            <Button disabled={loading} onClick={handleReset}>
              清空
            </Button>
          </Space>
        </Form>
      </Card>

      <Card title="任务进度">
        <Space direction="vertical" size={8} style={{ width: "100%" }}>
          <Progress
            percent={progressPercent}
            status={progressStatus}
            showInfo
          />

          <Text>{progress?.message || "暂无任务进度"}</Text>

          {typeof progress?.current === "number" &&
          typeof progress?.total === "number" ? (
            <Text type="secondary">
              当前进度：{progress.current} / {progress.total}
            </Text>
          ) : null}

          {progress?.chapterTitle ? (
            <Text type="secondary">当前章节：{progress.chapterTitle}</Text>
          ) : null}
        </Space>
      </Card>

      <Card title="执行结果">
        {resultData ? (
          <Descriptions bordered size="small" column={1}>
            <Descriptions.Item label="小说 ID">
              {resultData.novelId || "-"}
            </Descriptions.Item>

            <Descriptions.Item label="小说名称">
              {resultData.novelTitle || "-"}
            </Descriptions.Item>

            <Descriptions.Item label="章节总数">
              {resultData.chapterCount ?? "-"}
            </Descriptions.Item>

            <Descriptions.Item label="本次章节数">
              {resultData.selectedChapterCount ?? "-"}
            </Descriptions.Item>

            <Descriptions.Item label="成功数量">
              {resultData.successCount ?? "-"}
            </Descriptions.Item>

            <Descriptions.Item label="跳过数量">
              {resultData.skippedCount ?? "-"}
            </Descriptions.Item>

            <Descriptions.Item label="失败数量">
              {resultData.failedCount ?? "-"}
            </Descriptions.Item>

            <Descriptions.Item label="本次范围">
              {resultData.startIndex ?? "-"} - {resultData.endIndex ?? "末尾"}
            </Descriptions.Item>

            <Descriptions.Item label="下一次起始章节">
              {resultData.nextStartIndex ?? "-"}
            </Descriptions.Item>

            <Descriptions.Item label="是否被限制中断">
              {resultData.stoppedByRateLimit ? "是" : "否"}
            </Descriptions.Item>

            <Descriptions.Item label="保存根目录">
              {resultData.outputDir ? (
                <Text
                  copyable
                  style={{
                    cursor: "pointer",
                    color: "#1677ff",
                  }}
                  onClick={() => handleRevealPath(resultData.outputDir)}
                >
                  {resultData.outputDir}
                </Text>
              ) : (
                "-"
              )}
            </Descriptions.Item>

            <Descriptions.Item label="TXT 文件">
              {resultData.txtPath ? (
                <Text
                  copyable
                  style={{
                    cursor: "pointer",
                    color: "#1677ff",
                  }}
                  onClick={() => handleRevealPath(resultData.txtPath)}
                >
                  {resultData.txtPath}
                </Text>
              ) : (
                "-"
              )}
            </Descriptions.Item>

            <Descriptions.Item label="进度文件">
              {resultData.progressPath ? (
                <Text
                  copyable
                  style={{
                    cursor: "pointer",
                    color: "#1677ff",
                  }}
                  onClick={() => handleRevealPath(resultData.progressPath)}
                >
                  {resultData.progressPath}
                </Text>
              ) : (
                "-"
              )}
            </Descriptions.Item>

            <Descriptions.Item label="详情页">
              {resultData.novelDetailUrl || resultData.detailUrl || "-"}
            </Descriptions.Item>

            <Descriptions.Item label="章节列表页">
              {resultData.chapterListUrl || "-"}
            </Descriptions.Item>
          </Descriptions>
        ) : (
          <Text type="secondary">暂无执行结果</Text>
        )}
      </Card>

      {resultData?.failedChapters?.length ? (
        <Card title="失败章节">
          <Space direction="vertical" size={8} style={{ width: "100%" }}>
            {resultData.failedChapters.map((item, index) => (
              <Text key={`${item.index || index}-${item.title || ""}`}>
                {item.index || "-"} - {item.title || "-"}：{item.error || "-"}
              </Text>
            ))}
          </Space>
        </Card>
      ) : null}

      <PluginLogViewer logs={logs} />
    </Space>
  );
}
