import { useState } from "react";
import {
  Button,
  Card,
  Descriptions,
  Divider,
  Space,
  Switch,
  Table,
  Tag,
  Typography,
  message,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import { DeleteOutlined } from "@ant-design/icons";
import { selectFolder } from "@services/utils";
import { runTool } from "@services/toolRunner";
import { ToolPageLayout } from "@components/ToolPageLayout";
import { ToolPathPicker } from "@components/ToolPathPicker";

const { Text } = Typography;

interface EmptyFolderCleanerInput {
  sourceDir: string;
  dryRun?: boolean;
  recursive?: boolean;
}

interface EmptyFolderItem {
  path: string;
  status: "deleted" | "skipped" | "failed";
  reason?: string;
}

interface EmptyFolderCleanerData {
  sourceDir: string;
  scannedFolderCount: number;
  emptyFolderCount: number;
  deletedFolderCount: number;
  skippedFolderCount: number;
  failedCount: number;
  dryRun: boolean;
  items: EmptyFolderItem[];
}

const emptyFolderColumns: ColumnsType<EmptyFolderItem> = [
  {
    title: "文件夹路径",
    dataIndex: "path",
    key: "path",
    ellipsis: true,
  },
  {
    title: "状态",
    dataIndex: "status",
    key: "status",
    width: 120,
    render: (status: EmptyFolderItem["status"]) => {
      if (status === "deleted") {
        return <Tag color="green">已删除</Tag>;
      }

      if (status === "skipped") {
        return <Tag color="blue">已跳过</Tag>;
      }

      return <Tag color="red">失败</Tag>;
    },
  },
  {
    title: "原因",
    dataIndex: "reason",
    key: "reason",
    width: 240,
    render: (reason?: string) => reason || "-",
  },
];

export function EmptyFolderCleanerPage() {
  const [sourceDir, setSourceDir] = useState("");
  const [dryRun, setDryRun] = useState(true);
  const [recursive, setRecursive] = useState(true);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<EmptyFolderCleanerData | null>(null);

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

    try {
      setRunning(true);
      setResult(null);

      const response = await runTool<
        EmptyFolderCleanerInput,
        EmptyFolderCleanerData
      >({
        pluginId: "empty-folder-cleaner",
        input: {
          sourceDir,
          dryRun,
          recursive,
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
      setRunning(false);
    }
  }

  return (
    <ToolPageLayout
      title="空文件夹清理"
      description="扫描指定目录下的空文件夹，并支持预览或直接删除。建议先开启预览模式确认结果。"
      warning={{
        message: "删除操作不可恢复",
        description:
          "建议先使用预览模式查看将被清理的空文件夹，确认无误后再关闭预览模式执行删除。",
      }}
      result={result ? <EmptyFolderCleanerResult result={result} /> : null}
    >
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <ToolPathPicker
          label="目标文件夹"
          value={sourceDir}
          placeholder="请选择需要清理空文件夹的目录"
          onSelect={handleSelectFolder}
        />

        <Divider style={{ margin: "12px 0" }} />

        <Space direction="vertical" size={8}>
          <Text strong>执行选项</Text>

          <Space>
            <Switch checked={recursive} onChange={setRecursive} />
            <Text>递归扫描子文件夹</Text>
            <Tag color="blue">推荐</Tag>
          </Space>

          <Space>
            <Switch checked={dryRun} onChange={setDryRun} />
            <Text>仅预览，不实际删除</Text>
            <Tag color="orange">安全模式</Tag>
          </Space>
        </Space>

        <Divider style={{ margin: "12px 0" }} />

        <Button
          type="primary"
          danger={!dryRun}
          icon={<DeleteOutlined />}
          loading={running}
          disabled={!sourceDir}
          onClick={handleRun}
        >
          {dryRun ? "预览空文件夹" : "开始清理"}
        </Button>
      </Space>
    </ToolPageLayout>
  );
}

interface EmptyFolderCleanerResultProps {
  result: EmptyFolderCleanerData;
}

function EmptyFolderCleanerResult(props: EmptyFolderCleanerResultProps) {
  const { result } = props;

  return (
    <Card title={result.dryRun ? "预览结果" : "清理结果"}>
      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <Descriptions bordered column={2} size="middle">
          <Descriptions.Item label="源文件夹" span={2}>
            {result.sourceDir}
          </Descriptions.Item>

          <Descriptions.Item label="扫描文件夹数">
            {result.scannedFolderCount}
          </Descriptions.Item>

          <Descriptions.Item label="空文件夹数">
            {result.emptyFolderCount}
          </Descriptions.Item>

          <Descriptions.Item label="已删除数量">
            {result.deletedFolderCount}
          </Descriptions.Item>

          <Descriptions.Item label="已跳过数量">
            {result.skippedFolderCount}
          </Descriptions.Item>

          <Descriptions.Item label="失败数量">
            {result.failedCount}
          </Descriptions.Item>

          <Descriptions.Item label="执行模式">
            {result.dryRun ? (
              <Tag color="orange">仅预览</Tag>
            ) : (
              <Tag color="red">实际删除</Tag>
            )}
          </Descriptions.Item>
        </Descriptions>

        {result.items.length > 0 ? (
          <Table
            rowKey="path"
            size="small"
            columns={emptyFolderColumns}
            dataSource={result.items}
            pagination={{ pageSize: 8 }}
          />
        ) : null}
      </Space>
    </Card>
  );
}
