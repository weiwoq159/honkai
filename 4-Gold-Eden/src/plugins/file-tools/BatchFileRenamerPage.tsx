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
  Radio,
  Space,
  Switch,
  Typography,
  message,
} from "antd";
import {
  ClearOutlined,
  EditOutlined,
  FileTextOutlined,
  FolderOpenOutlined,
  NumberOutlined,
} from "@ant-design/icons";
import { open } from "@tauri-apps/plugin-dialog";

import { PluginLogViewer } from "../components/PluginLogViewer";
import {
  listenToolLog,
  listenToolProgress,
  runTool,
} from "../../services/toolRunner";

const { Text } = Typography;

type RenameMode = "replace" | "prefix" | "suffix" | "sequence";

interface BatchFileRenamerFormValues {
  folderPath: string;
  mode: RenameMode;
  keyword: string;
  replacement: string;
  prefix: string;
  suffix: string;
  sequenceName: string;
  startNumber: number;
  padding: number;
  includeSubfolders: boolean;
  dryRun: boolean;
}

interface BatchFileRenamerData {
  action?: string;
  folderPath?: string;
  total?: number;
  renamed?: number;
  skipped?: number;
  failed?: number;
  preview?: Array<{
    oldPath: string;
    newPath: string;
  }>;
  logs?: string[];
}

interface BatchFileRenamerProgress {
  stage:
    | "preparing"
    | "scanning"
    | "previewing"
    | "renaming"
    | "completed"
    | "error";

  percent: number;
  current?: number;
  total?: number;
  fileName?: string;
  message?: string;
}

function getProgressStatus(
  loading: boolean,
  progress: BatchFileRenamerProgress | null,
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

export function BatchFileRenamerPage() {
  const [form] = Form.useForm<BatchFileRenamerFormValues>();

  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [resultData, setResultData] = useState<BatchFileRenamerData | null>(
    null,
  );
  const [progress, setProgress] = useState<BatchFileRenamerProgress | null>(
    null,
  );

  const mode = Form.useWatch("mode", form);

  useEffect(() => {
    const unlistenList: Array<() => void> = [];

    listenToolProgress<BatchFileRenamerProgress>((payload) => {
      if (payload.pluginId !== "batch-file-renamer") {
        return;
      }

      setProgress(payload.data);
    }).then((unlisten) => {
      unlistenList.push(unlisten);
    });

    listenToolLog<string>((payload) => {
      if (payload.pluginId !== "batch-file-renamer") {
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

  async function handleSelectFolder() {
    try {
      const selected = await open({
        directory: true,
        multiple: false,
        title: "选择需要批量重命名的文件夹",
      });

      if (!selected) {
        return;
      }

      const folderPath = Array.isArray(selected) ? selected[0] : selected;

      if (!folderPath) {
        return;
      }

      form.setFieldsValue({
        folderPath,
      });

      await form.validateFields(["folderPath"]);
    } catch (error) {
      console.error(error);
      message.error("选择文件夹失败");
    }
  }

  async function handleRun(values: BatchFileRenamerFormValues) {
    try {
      setLoading(true);
      setLogs([]);
      setResultData(null);
      setProgress({
        stage: "preparing",
        percent: 0,
        message: "准备开始批量重命名任务",
      });

      const result = await runTool<BatchFileRenamerData>({
        pluginId: "batch-file-renamer",
        input: {
          action: "run",
          config: {
            folderPath: values.folderPath.trim(),
            mode: values.mode,
            keyword: values.keyword?.trim() || "",
            replacement: values.replacement?.trim() || "",
            prefix: values.prefix?.trim() || "",
            suffix: values.suffix?.trim() || "",
            sequenceName: values.sequenceName?.trim() || "",
            startNumber: values.startNumber ?? 1,
            padding: values.padding ?? 3,
            includeSubfolders: Boolean(values.includeSubfolders),
            dryRun: Boolean(values.dryRun),
          },
        },
      });

      const rawData = result.data as any;

      const normalizedData: BatchFileRenamerData | null =
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
          stage: "completed",
          percent: 100,
          current: prevProgress?.total,
          total: prevProgress?.total,
          message: values.dryRun ? "预览任务执行完成" : "批量重命名执行完成",
        }));

        message.success(result.message || "批量重命名执行完成");
      } else {
        setProgress((prevProgress) => ({
          stage: "error",
          percent: prevProgress?.percent || 0,
          message: result.message || "批量重命名执行失败",
        }));

        message.error(result.message || "批量重命名执行失败");
      }
    } catch (error) {
      console.error(error);

      const errorMessage =
        error instanceof Error
          ? error.message
          : typeof error === "string"
            ? error
            : "批量重命名执行异常";

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
        description="选择本地文件夹后，根据规则批量重命名文件。建议先开启预览模式确认结果，避免误操作。"
      />

      <Card title="重命名配置">
        <Form
          form={form}
          layout="vertical"
          onFinish={handleRun}
          initialValues={{
            folderPath: "",
            mode: "replace",
            keyword: "",
            replacement: "",
            prefix: "",
            suffix: "",
            sequenceName: "file",
            startNumber: 1,
            padding: 3,
            includeSubfolders: false,
            dryRun: true,
          }}
        >
          <Form.Item label="目标文件夹" required>
            <Space.Compact style={{ width: "100%" }}>
              <Form.Item
                name="folderPath"
                noStyle
                rules={[
                  {
                    required: true,
                    message: "请选择需要重命名的文件夹",
                  },
                ]}
              >
                <Input
                  prefix={<FolderOpenOutlined />}
                  placeholder="请选择需要批量重命名的文件夹"
                  allowClear
                  readOnly
                  disabled={loading}
                />
              </Form.Item>

              <Button
                htmlType="button"
                icon={<FolderOpenOutlined />}
                disabled={loading}
                onClick={handleSelectFolder}
              >
                选择文件夹
              </Button>
            </Space.Compact>
          </Form.Item>

          <Form.Item
            label="重命名模式"
            name="mode"
            rules={[
              {
                required: true,
                message: "请选择重命名模式",
              },
            ]}
          >
            <Radio.Group disabled={loading}>
              <Radio.Button value="replace">查找替换</Radio.Button>
              <Radio.Button value="prefix">添加前缀</Radio.Button>
              <Radio.Button value="suffix">添加后缀</Radio.Button>
              <Radio.Button value="sequence">序号命名</Radio.Button>
            </Radio.Group>
          </Form.Item>

          {mode === "replace" ? (
            <Space size={12} style={{ width: "100%" }} align="start">
              <Form.Item
                label="查找内容"
                name="keyword"
                style={{ flex: 1 }}
                rules={[
                  {
                    required: true,
                    message: "请输入需要查找的内容",
                  },
                ]}
              >
                <Input
                  prefix={<FileTextOutlined />}
                  placeholder="例如：IMG_"
                  allowClear
                  disabled={loading}
                />
              </Form.Item>

              <Form.Item label="替换为" name="replacement" style={{ flex: 1 }}>
                <Input
                  prefix={<EditOutlined />}
                  placeholder="例如：photo_"
                  allowClear
                  disabled={loading}
                />
              </Form.Item>
            </Space>
          ) : null}

          {mode === "prefix" ? (
            <Form.Item
              label="前缀内容"
              name="prefix"
              rules={[
                {
                  required: true,
                  message: "请输入前缀内容",
                },
              ]}
            >
              <Input
                prefix={<EditOutlined />}
                placeholder="例如：new_"
                allowClear
                disabled={loading}
              />
            </Form.Item>
          ) : null}

          {mode === "suffix" ? (
            <Form.Item
              label="后缀内容"
              name="suffix"
              rules={[
                {
                  required: true,
                  message: "请输入后缀内容",
                },
              ]}
            >
              <Input
                prefix={<EditOutlined />}
                placeholder="例如：_backup"
                allowClear
                disabled={loading}
              />
            </Form.Item>
          ) : null}

          {mode === "sequence" ? (
            <Space size={12} style={{ width: "100%" }} align="start">
              <Form.Item
                label="基础名称"
                name="sequenceName"
                style={{ flex: 1 }}
                rules={[
                  {
                    required: true,
                    message: "请输入基础名称",
                  },
                ]}
              >
                <Input
                  prefix={<FileTextOutlined />}
                  placeholder="例如：image"
                  allowClear
                  disabled={loading}
                />
              </Form.Item>

              <Form.Item
                label="起始序号"
                name="startNumber"
                style={{ width: 140 }}
                rules={[
                  {
                    required: true,
                    message: "请输入起始序号",
                  },
                ]}
              >
                <InputNumber
                  min={0}
                  precision={0}
                  style={{ width: "100%" }}
                  prefix={<NumberOutlined />}
                  disabled={loading}
                />
              </Form.Item>

              <Form.Item
                label="补零位数"
                name="padding"
                style={{ width: 140 }}
                rules={[
                  {
                    required: true,
                    message: "请输入补零位数",
                  },
                ]}
              >
                <InputNumber
                  min={1}
                  max={10}
                  precision={0}
                  style={{ width: "100%" }}
                  disabled={loading}
                />
              </Form.Item>
            </Space>
          ) : null}

          <Space size={24} style={{ marginBottom: 24 }}>
            <Form.Item
              label="包含子文件夹"
              name="includeSubfolders"
              valuePropName="checked"
              style={{ marginBottom: 0 }}
            >
              <Switch disabled={loading} />
            </Form.Item>

            <Form.Item
              label="预览模式"
              name="dryRun"
              valuePropName="checked"
              style={{ marginBottom: 0 }}
            >
              <Switch disabled={loading} />
            </Form.Item>
          </Space>

          <Form.Item style={{ marginBottom: 0 }}>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<EditOutlined />}
                loading={loading}
              >
                开始执行
              </Button>

              <Button
                disabled={loading}
                icon={<ClearOutlined />}
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

          {progress?.fileName ? (
            <Text type="secondary">当前文件：{progress.fileName}</Text>
          ) : null}
        </Space>
      </Card>

      <Card title="执行结果">
        {resultData ? (
          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="目标文件夹">
              <Text copyable={!!resultData.folderPath}>
                {resultData.folderPath || "-"}
              </Text>
            </Descriptions.Item>

            <Descriptions.Item label="文件总数">
              {resultData.total ?? "-"}
            </Descriptions.Item>

            <Descriptions.Item label="已重命名">
              {resultData.renamed ?? "-"}
            </Descriptions.Item>

            <Descriptions.Item label="已跳过">
              {resultData.skipped ?? "-"}
            </Descriptions.Item>

            <Descriptions.Item label="失败数量">
              {resultData.failed ?? "-"}
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
