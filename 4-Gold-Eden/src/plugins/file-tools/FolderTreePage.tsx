import { useState } from "react";
import {
  Alert,
  Button,
  Card,
  Descriptions,
  Form,
  Input,
  InputNumber,
  Space,
  Switch,
  Typography,
  message,
} from "antd";
import {
  ClearOutlined,
  CopyOutlined,
  FolderOpenOutlined,
  PlayCircleOutlined,
} from "@ant-design/icons";
import { open } from "@tauri-apps/plugin-dialog";
import { runTool } from "@services/toolRunner";

const { Title, Paragraph, Text } = Typography;

interface FolderTreeConfig {
  folderPath: string;
  maxDepth: number;
  includeFiles: boolean;
  includeHidden: boolean;
}

interface FolderTreeData {
  folderPath?: string;
  totalDirs?: number;
  totalFiles?: number;
  markdown?: string;
  logs?: string[];
}

export function FolderTreePage() {
  const [form] = Form.useForm<FolderTreeConfig>();

  const [loading, setLoading] = useState(false);
  const [markdown, setMarkdown] = useState("");
  const [resultData, setResultData] = useState<FolderTreeData | null>(null);

  async function handleSelectFolder() {
    try {
      const selected = await open({
        directory: true,
        multiple: false,
        title: "选择需要查看目录结构的文件夹",
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

  async function handleRun(values: FolderTreeConfig) {
    try {
      setLoading(true);
      setMarkdown("");
      setResultData(null);

      const config: FolderTreeConfig = {
        folderPath: values.folderPath.trim(),
        maxDepth: values.maxDepth ?? 3,
        includeFiles: Boolean(values.includeFiles),
        includeHidden: Boolean(values.includeHidden),
      };

      const result = await runTool<FolderTreeData, FolderTreeConfig>({
        pluginId: "folder-tree",
        input: {
          action: "run",
          config,
        },
      });

      if (!result.success) {
        console.log(result.message);

        message.error(result.message || "目录结构获取失败");
        return;
      }

      if (!result.data?.markdown) {
        message.warning("插件执行成功，但没有返回 markdown 数据");
        setResultData(result.data ?? null);
        return;
      }

      setMarkdown(result.data.markdown);
      setResultData(result.data);

      message.success(result.message || "目录结构获取完成");
    } catch (error) {
      console.error(error);

      const errorMessage =
        error instanceof Error
          ? error.message
          : typeof error === "string"
            ? error
            : "目录结构获取异常";

      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }

  async function handleCopy() {
    if (!markdown) {
      message.warning("暂无可复制内容");
      return;
    }

    try {
      await navigator.clipboard.writeText(markdown);
      message.success("已复制 Markdown 内容");
    } catch (error) {
      console.error(error);
      message.error("复制失败");
    }
  }

  function handleClear() {
    form.resetFields();
    setMarkdown("");
    setResultData(null);
  }

  return (
    <Space direction="vertical" size={16} style={{ width: "100%" }}>
      <Card>
        <Title level={3} style={{ marginTop: 0 }}>
          目录结构查看
        </Title>

        <Paragraph type="secondary">
          获取指定文件夹的目录结构，并以 Markdown
          格式返回，适合复制到文档、README 或交给 AI 分析项目结构。
        </Paragraph>

        <Alert
          type="info"
          showIcon
          message="工具说明"
          description="如果目标文件夹很大，建议先限制扫描深度，避免一次性遍历过多文件导致卡顿。"
        />
      </Card>

      <Card title="扫描配置">
        <Form
          form={form}
          layout="vertical"
          onFinish={handleRun}
          initialValues={{
            folderPath: "",
            maxDepth: 3,
            includeFiles: true,
            includeHidden: false,
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
                    message: "请选择需要查看目录结构的文件夹",
                  },
                ]}
              >
                <Input
                  prefix={<FolderOpenOutlined />}
                  placeholder="请选择需要查看目录结构的文件夹"
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
            label="扫描深度"
            name="maxDepth"
            rules={[
              {
                required: true,
                message: "请输入扫描深度",
              },
            ]}
          >
            <InputNumber
              min={1}
              max={20}
              precision={0}
              style={{ width: 240 }}
              addonAfter="层"
              disabled={loading}
            />
          </Form.Item>

          <Space size={24} style={{ marginBottom: 24 }}>
            <Form.Item
              label="包含文件"
              name="includeFiles"
              valuePropName="checked"
              style={{ marginBottom: 0 }}
            >
              <Switch disabled={loading} />
            </Form.Item>

            <Form.Item
              label="包含隐藏文件"
              name="includeHidden"
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
                icon={<PlayCircleOutlined />}
                loading={loading}
              >
                生成目录结构
              </Button>

              <Button
                htmlType="button"
                disabled={loading}
                icon={<ClearOutlined />}
                onClick={handleClear}
              >
                清空
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <Card title="扫描结果">
        {resultData ? (
          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="目标文件夹">
              <Text copyable={!!resultData.folderPath}>
                {resultData.folderPath || "-"}
              </Text>
            </Descriptions.Item>

            <Descriptions.Item label="文件夹数量">
              {resultData.totalDirs ?? "-"}
            </Descriptions.Item>

            <Descriptions.Item label="文件数量">
              {resultData.totalFiles ?? "-"}
            </Descriptions.Item>
          </Descriptions>
        ) : (
          <Text type="secondary">暂无扫描结果</Text>
        )}
      </Card>

      <Card
        title="Markdown 目录结构"
        extra={
          <Button icon={<CopyOutlined />} onClick={handleCopy}>
            复制 Markdown
          </Button>
        }
      >
        {markdown ? (
          <pre
            style={{
              margin: 0,
              padding: 16,
              background: "#f6f8fa",
              borderRadius: 8,
              overflow: "auto",
              maxHeight: 600,
              lineHeight: 1.6,
            }}
          >
            <code>{markdown}</code>
          </pre>
        ) : (
          <Text type="secondary">
            暂无目录结构。请选择文件夹后点击“生成目录结构”。
          </Text>
        )}
      </Card>
    </Space>
  );
}
