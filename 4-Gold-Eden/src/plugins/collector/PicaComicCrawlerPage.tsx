import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Descriptions,
  Form,
  Input,
  Progress,
  Space,
  Typography,
  message,
} from "antd";
import {
  CloudDownloadOutlined,
  LinkOutlined,
  LockOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { PluginLogViewer } from "../components/PluginLogViewer";
import {
  listenToolLog,
  listenToolProgress,
  runTool,
} from "../../services/toolRunner";

const { Paragraph, Text } = Typography;

interface PicaComicCrawlerData {
  action?: string;
  comicId?: string;
  title?: string;
  comicDir?: string;
  chapterCount?: number;
  imageCount?: number;
  logs?: string[];
}

interface PicaComicCrawlerFormValues {
  email: string;
  password: string;
  comicUrl: string;
}

interface PicaComicCrawlerProgress {
  stage:
    | "preparing"
    | "login"
    | "fetching_detail"
    | "fetching_chapters"
    | "fetching_images"
    | "downloading"
    | "completed"
    | "error";

  percent: number;
  current?: number;
  total?: number;
  chapterOrder?: number;
  chapterTitle?: string;
  message?: string;
}

function getProgressStatus(
  loading: boolean,
  progress: PicaComicCrawlerProgress | null,
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

export function PicaComicCrawlerPage() {
  const [form] = Form.useForm<PicaComicCrawlerFormValues>();

  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [resultData, setResultData] = useState<PicaComicCrawlerData | null>(
    null,
  );
  const [progress, setProgress] = useState<PicaComicCrawlerProgress | null>(
    null,
  );

  useEffect(() => {
    const unlistenList: Array<() => void> = [];

    listenToolProgress<PicaComicCrawlerProgress>((payload) => {
      if (payload.pluginId !== "pica-comic-crawler") {
        return;
      }

      setProgress(payload.data);
    }).then((unlisten) => {
      unlistenList.push(unlisten);
    });

    listenToolLog<string>((payload) => {
      if (payload.pluginId !== "pica-comic-crawler") {
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

  async function handleRun(values: PicaComicCrawlerFormValues) {
    try {
      setLoading(true);
      setLogs([]);
      setResultData(null);
      setProgress({
        stage: "preparing",
        percent: 0,
        message: "准备开始采集任务",
      });

      const result = await runTool<PicaComicCrawlerData>({
        pluginId: "pica-comic-crawler",
        input: {
          action: "run",
          config: {
            email: values.email.trim(),
            password: values.password,
            comicUrl: values.comicUrl.trim(),
          },
        },
      });

      const resultLogs = result.logs || result.data?.logs || [];

      if (resultLogs.length > 0) {
        setLogs(resultLogs);
      }

      setResultData(result.data || null);

      if (result.success) {
        setProgress((prevProgress) => ({
          stage: "completed",
          percent: 100,
          current: prevProgress?.total,
          total: prevProgress?.total,
          message: "采集任务执行完成",
        }));

        message.success(result.message || "采集任务执行完成");
      } else {
        setProgress((prevProgress) => ({
          stage: "error",
          percent: prevProgress?.percent || 0,
          message: result.message || "采集任务执行失败",
        }));

        message.error(result.message || "采集任务执行失败");
      }
    } catch (error) {
      console.error(error);

      const errorMessage =
        error instanceof Error ? error.message : "采集任务执行异常";

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

  const progressPercent = progress?.percent ?? 0;
  const progressStatus = getProgressStatus(loading, progress);

  return (
    <Space direction="vertical" size={16} style={{ width: "100%" }}>
      <Alert
        type="info"
        showIcon
        message="工具说明"
        description="根据账号信息和漫画详情页地址，调用本地 Python 插件采集漫画章节与图片信息。账号密码只会传递给本地插件处理，请不要在日志中打印明文密码。"
      />

      <Card title="采集配置">
        <Form
          form={form}
          layout="vertical"
          onFinish={handleRun}
          initialValues={{
            email: "",
            password: "",
            comicUrl: "",
          }}
        >
          <Form.Item
            label="账号 / 邮箱"
            name="email"
            rules={[
              {
                required: true,
                message: "请输入账号或邮箱",
              },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="请输入账号或邮箱"
              allowClear
              disabled={loading}
            />
          </Form.Item>

          <Form.Item
            label="密码"
            name="password"
            rules={[
              {
                required: true,
                message: "请输入密码",
              },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="请输入密码"
              allowClear
              disabled={loading}
            />
          </Form.Item>

          <Form.Item
            label="漫画地址"
            name="comicUrl"
            rules={[
              {
                required: true,
                message: "请输入漫画地址",
              },
              {
                validator: (_, value) => {
                  if (!value) {
                    return Promise.resolve();
                  }

                  const text = String(value).trim();

                  if (
                    text.startsWith("http://") ||
                    text.startsWith("https://") ||
                    text.length >= 10
                  ) {
                    return Promise.resolve();
                  }

                  return Promise.reject(new Error("请输入有效的漫画地址"));
                },
              },
            ]}
          >
            <Input
              prefix={<LinkOutlined />}
              placeholder="例如：https://manhuabika.com/comic/xxxx"
              allowClear
              disabled={loading}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0 }}>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<CloudDownloadOutlined />}
                loading={loading}
              >
                开始采集
              </Button>

              <Button
                disabled={loading}
                onClick={() => {
                  form.resetFields();
                  setLogs([]);
                  setResultData(null);
                  setProgress(null);
                }}
              >
                清空
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <Card title="任务进度">
        <Space direction="vertical" size={8} style={{ width: "100%" }}>
          <Progress percent={progressPercent} status={progressStatus} />

          <Text type="secondary">{progress?.message || "暂无任务进度"}</Text>

          {typeof progress?.current === "number" &&
          typeof progress?.total === "number" ? (
            <Text type="secondary">
              当前进度：{progress.current} / {progress.total}
            </Text>
          ) : null}

          {progress?.chapterTitle ? (
            <Text type="secondary">
              当前章节：{progress.chapterOrder || "-"} - {progress.chapterTitle}
            </Text>
          ) : null}
        </Space>
      </Card>

      <Card title="执行结果">
        {resultData ? (
          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="漫画 ID">
              {resultData.comicId || "-"}
            </Descriptions.Item>

            <Descriptions.Item label="漫画标题">
              {resultData.title || "-"}
            </Descriptions.Item>

            <Descriptions.Item label="章节数量">
              {resultData.chapterCount ?? "-"}
            </Descriptions.Item>

            <Descriptions.Item label="图片数量">
              {resultData.imageCount ?? "-"}
            </Descriptions.Item>

            <Descriptions.Item label="保存目录">
              <Text copyable={!!resultData.comicDir}>
                {resultData.comicDir || "-"}
              </Text>
            </Descriptions.Item>
          </Descriptions>
        ) : (
          <Text type="secondary">暂无执行结果</Text>
        )}
      </Card>

      <PluginLogViewer logs={logs} />
    </Space>
  );
}
