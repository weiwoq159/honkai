import { useState } from "react";
import {
  Button,
  Card,
  Descriptions,
  Divider,
  Input,
  Space,
  Statistic,
  Switch,
  Table,
  Tag,
  Typography,
  message,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import { FolderOutlined } from "@ant-design/icons";
import { selectFolder } from "@services/utils";
import { runTool } from "@services/toolRunner";
import { ToolPageLayout } from "@components/ToolPageLayout";
import { ToolPathPicker } from "@components/ToolPathPicker";

const { Text } = Typography;

interface FileTypeOrganizerInput {
  sourceDir: string;
  dryRun: boolean;
  recursive: boolean;
  conflictStrategy: "rename" | "skip";
  noExtensionFolderName: string;
}

interface FileTypeOrganizerItem {
  sourcePath: string;
  targetPath: string;
  extension: string;
  status: "moved" | "skipped" | "failed";
  reason?: string;
}

interface FileTypeOrganizerData {
  sourceDir: string;
  dryRun: boolean;
  recursive: boolean;
  conflictStrategy: "rename" | "skip";
  scannedFileCount: number;
  movedFileCount: number;
  skippedFileCount: number;
  failedCount: number;
  typeCount: number;
  items: FileTypeOrganizerItem[];
}

function formatStatus(status: FileTypeOrganizerItem["status"]) {
  if (status === "moved") {
    return <Tag color="green">已移动</Tag>;
  }

  if (status === "skipped") {
    return <Tag color="blue">已跳过</Tag>;
  }

  return <Tag color="red">失败</Tag>;
}

const fileTypeOrganizerColumns: ColumnsType<FileTypeOrganizerItem> = [
  {
    title: "文件类型",
    dataIndex: "extension",
    key: "extension",
    width: 140,
    render: (extension: string) => {
      if (extension === "[no-extension]") {
        return <Tag>无扩展名</Tag>;
      }

      return <Tag color="blue">{extension}</Tag>;
    },
  },
  {
    title: "源路径",
    dataIndex: "sourcePath",
    key: "sourcePath",
    ellipsis: true,
  },
  {
    title: "目标路径",
    dataIndex: "targetPath",
    key: "targetPath",
    ellipsis: true,
  },
  {
    title: "状态",
    dataIndex: "status",
    key: "status",
    width: 120,
    render: formatStatus,
  },
  {
    title: "原因",
    dataIndex: "reason",
    key: "reason",
    width: 220,
    render: (reason?: string) => reason || "-",
  },
];

export function FileTypeOrganizerPage() {
  const [sourceDir, setSourceDir] = useState("");
  const [dryRun, setDryRun] = useState(true);
  const [recursive, setRecursive] = useState(false);
  const [noExtensionFolderName, setNoExtensionFolderName] =
    useState("no-extension");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<FileTypeOrganizerData | null>(null);

  async function handleSelectFolder() {
    const selected = await selectFolder();

    if (!selected) {
      return;
    }

    setSourceDir(selected);
    setResult(null);
  }

  async function handleRun() {
    if (!sourceDir) {
      message.warning("请先选择文件夹");
      return;
    }

    if (!noExtensionFolderName.trim()) {
      message.warning("无扩展名文件夹名称不能为空");
      return;
    }

    try {
      setLoading(true);
      setResult(null);

      const response = await runTool<
        FileTypeOrganizerInput,
        FileTypeOrganizerData
      >({
        pluginId: "file-type-organizer",
        input: {
          sourceDir,
          dryRun,
          recursive,
          conflictStrategy: "rename",
          noExtensionFolderName: noExtensionFolderName.trim(),
        },
      });

      if (!response.success || !response.data) {
        message.error(response.message);
        return;
      }

      setResult(response.data);
      message.success(response.message);
    } catch (error) {
      console.error(error);
      message.error("执行失败，请查看控制台日志");
    } finally {
      setLoading(false);
    }
  }

  return (
    <ToolPageLayout
      title="按文件类型分类整理"
      description="按文件扩展名将指定目录下的文件分类移动到对应文件夹中，例如 jpg、png、mp4、pdf。"
      warning={{
        message: "该操作会移动文件位置",
        description:
          "建议先开启预览模式确认整理结果。确认无误后再关闭预览模式执行实际移动。",
      }}
      result={result ? <FileTypeOrganizerResult result={result} /> : null}
    >
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <ToolPathPicker
          label="目标文件夹"
          value={sourceDir}
          placeholder="请选择需要按文件类型整理的文件夹"
          onSelect={handleSelectFolder}
        />

        <Divider style={{ margin: "12px 0" }} />

        <Space direction="vertical" size={8}>
          <Text strong>执行选项</Text>

          <Space>
            <Switch checked={dryRun} onChange={setDryRun} />
            <Text>仅预览，不实际移动</Text>
            <Tag color="orange">安全模式</Tag>
          </Space>

          <Space>
            <Switch checked={recursive} onChange={setRecursive} />
            <Text>递归整理子文件夹中的文件</Text>
          </Space>

          <Space>
            <Switch checked disabled />
            <Text>文件名冲突时自动重命名</Text>
            <Tag color="blue">推荐</Tag>
          </Space>

          <Space>
            <Text>无扩展名文件夹名称</Text>
            <Input
              style={{ width: 220 }}
              value={noExtensionFolderName}
              onChange={(event) => setNoExtensionFolderName(event.target.value)}
            />
          </Space>
        </Space>

        <Divider style={{ margin: "12px 0" }} />

        <Button
          type="primary"
          danger={!dryRun}
          icon={<FolderOutlined />}
          loading={loading}
          disabled={!sourceDir}
          onClick={handleRun}
        >
          {dryRun ? "预览整理结果" : "开始整理"}
        </Button>
      </Space>
    </ToolPageLayout>
  );
}

interface FileTypeOrganizerResultProps {
  result: FileTypeOrganizerData;
}

function FileTypeOrganizerResult(props: FileTypeOrganizerResultProps) {
  const { result } = props;

  return (
    <Card title={result.dryRun ? "预览结果" : "整理结果"}>
      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <Space wrap size={16}>
          <Card size="small">
            <Statistic title="扫描文件数" value={result.scannedFileCount} />
          </Card>

          <Card size="small">
            <Statistic title="涉及类型数" value={result.typeCount} />
          </Card>

          <Card size="small">
            <Statistic title="移动文件数" value={result.movedFileCount} />
          </Card>

          <Card size="small">
            <Statistic title="跳过文件数" value={result.skippedFileCount} />
          </Card>

          <Card size="small">
            <Statistic title="失败数量" value={result.failedCount} />
          </Card>
        </Space>

        <Descriptions bordered column={2} size="middle">
          <Descriptions.Item label="源文件夹" span={2}>
            {result.sourceDir}
          </Descriptions.Item>

          <Descriptions.Item label="执行模式">
            {result.dryRun ? (
              <Tag color="orange">仅预览</Tag>
            ) : (
              <Tag color="red">实际移动</Tag>
            )}
          </Descriptions.Item>

          <Descriptions.Item label="递归整理">
            {result.recursive ? "是" : "否"}
          </Descriptions.Item>

          <Descriptions.Item label="冲突处理">
            {result.conflictStrategy === "rename" ? "自动重命名" : "跳过"}
          </Descriptions.Item>

          <Descriptions.Item label="涉及类型数">
            {result.typeCount}
          </Descriptions.Item>

          <Descriptions.Item label="扫描文件数">
            {result.scannedFileCount}
          </Descriptions.Item>

          <Descriptions.Item label="移动文件数">
            {result.movedFileCount}
          </Descriptions.Item>

          <Descriptions.Item label="跳过文件数">
            {result.skippedFileCount}
          </Descriptions.Item>

          <Descriptions.Item label="失败数量">
            {result.failedCount}
          </Descriptions.Item>
        </Descriptions>

        {result.items.length > 0 ? (
          <>
            <Divider />

            <Table
              rowKey={(record) => `${record.sourcePath}-${record.targetPath}`}
              size="small"
              columns={fileTypeOrganizerColumns}
              dataSource={result.items}
              pagination={{ pageSize: 10 }}
            />
          </>
        ) : null}
      </Space>
    </Card>
  );
}
