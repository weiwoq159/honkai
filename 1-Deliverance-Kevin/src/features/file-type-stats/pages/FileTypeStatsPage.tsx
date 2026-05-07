import { useState } from "react";
import {
  Button,
  Card,
  Descriptions,
  Divider,
  InputNumber,
  Space,
  Statistic,
  Table,
  Tag,
  Typography,
  message,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import { SearchOutlined } from "@ant-design/icons";
import { selectFolder } from "@services/utils";
import { runTool } from "@services/toolRunner";
import { ToolPageLayout } from "@components/ToolPageLayout";
import { ToolPathPicker } from "@components/ToolPathPicker";

const { Text } = Typography;

interface FileTypeStatsInput {
  sourceDir: string;
  limit: number;
}

interface FileTypeItem {
  extension: string;
  fileCount: number;
  totalSize: number;
  sizeMb: number;
}

interface FileTypeStatsData {
  sourceDir: string;
  totalFileCount: number;
  totalSize: number;
  typeCount: number;
  limit: number;
  items: FileTypeItem[];
  failedCount?: number;
  failedItems?: Array<{
    path: string;
    reason: string;
  }>;
}

function formatBytes(bytes: number): string {
  if (!bytes) return "0 B";

  const units = ["B", "KB", "MB", "GB", "TB"];
  let value = bytes;
  let index = 0;

  while (value >= 1024 && index < units.length - 1) {
    value /= 1024;
    index += 1;
  }

  return `${value.toFixed(2)} ${units[index]}`;
}

const fileTypeColumns: ColumnsType<FileTypeItem> = [
  {
    title: "文件类型",
    dataIndex: "extension",
    key: "extension",
    width: 160,
    render: (extension: string) => {
      if (extension === "[no-extension]") {
        return <Tag>无扩展名</Tag>;
      }

      return <Tag color="blue">{extension}</Tag>;
    },
  },
  {
    title: "文件数量",
    dataIndex: "fileCount",
    key: "fileCount",
    width: 140,
    sorter: (a, b) => a.fileCount - b.fileCount,
  },
  {
    title: "总大小",
    dataIndex: "totalSize",
    key: "totalSize",
    width: 160,
    defaultSortOrder: "descend",
    sorter: (a, b) => a.totalSize - b.totalSize,
    render: (totalSize: number) => formatBytes(totalSize),
  },
  {
    title: "大小 MB",
    dataIndex: "sizeMb",
    key: "sizeMb",
    width: 120,
    sorter: (a, b) => a.sizeMb - b.sizeMb,
  },
];

export function FileTypeStatsPage() {
  const [sourceDir, setSourceDir] = useState("");
  const [limit, setLimit] = useState(100);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<FileTypeStatsData | null>(null);

  async function handleSelectFolder() {
    const selected = await selectFolder();

    if (!selected) {
      return;
    }

    setSourceDir(selected);
    setResult(null);
  }

  async function handleScan() {
    if (!sourceDir) {
      message.warning("请先选择文件夹");
      return;
    }

    try {
      setLoading(true);
      setResult(null);

      const response = await runTool<FileTypeStatsInput, FileTypeStatsData>({
        pluginId: "file-type-stats",
        input: {
          sourceDir,
          limit,
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
      title="文件类型统计"
      description="扫描指定目录下的文件类型分布，统计不同扩展名的文件数量和占用空间。"
      warning={{
        message: "该功能只读取文件信息，不会修改文件",
        description:
          "扫描结果会按占用空间倒序展示。文件数量较多时可能需要等待一段时间。",
      }}
      result={result ? <FileTypeStatsResult result={result} /> : null}
    >
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <ToolPathPicker
          label="目标文件夹"
          value={sourceDir}
          placeholder="请选择需要统计文件类型的文件夹"
          onSelect={handleSelectFolder}
        />

        <Divider style={{ margin: "12px 0" }} />

        <Space wrap>
          <Text strong>扫描选项</Text>

          <Text>最多展示类型数量</Text>
          <InputNumber
            min={1}
            max={10000}
            value={limit}
            onChange={(value) => setLimit(value ?? 100)}
          />
        </Space>

        <Divider style={{ margin: "12px 0" }} />

        <Button
          type="primary"
          icon={<SearchOutlined />}
          loading={loading}
          disabled={!sourceDir}
          onClick={handleScan}
        >
          开始统计
        </Button>
      </Space>
    </ToolPageLayout>
  );
}

interface FileTypeStatsResultProps {
  result: FileTypeStatsData;
}

function FileTypeStatsResult(props: FileTypeStatsResultProps) {
  const { result } = props;

  return (
    <Card title="统计结果">
      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <Space wrap size={16}>
          <Card size="small">
            <Statistic title="文件总数" value={result.totalFileCount} />
          </Card>

          <Card size="small">
            <Statistic title="文件类型数" value={result.typeCount} />
          </Card>

          <Card size="small">
            <Statistic
              title="文件总大小"
              value={formatBytes(result.totalSize)}
            />
          </Card>

          <Card size="small">
            <Statistic title="读取失败数" value={result.failedCount ?? 0} />
          </Card>
        </Space>

        <Descriptions bordered column={2} size="middle">
          <Descriptions.Item label="文件夹路径" span={2}>
            {result.sourceDir}
          </Descriptions.Item>

          <Descriptions.Item label="文件总数">
            {result.totalFileCount}
          </Descriptions.Item>

          <Descriptions.Item label="文件类型数">
            {result.typeCount}
          </Descriptions.Item>

          <Descriptions.Item label="文件总大小">
            {formatBytes(result.totalSize)}
          </Descriptions.Item>

          <Descriptions.Item label="最多展示数量">
            {result.limit}
          </Descriptions.Item>

          <Descriptions.Item label="读取失败数量">
            {result.failedCount ?? 0}
          </Descriptions.Item>
        </Descriptions>

        {result.items.length > 0 ? (
          <>
            <Divider />

            <Table
              rowKey="extension"
              size="small"
              columns={fileTypeColumns}
              dataSource={result.items}
              pagination={{ pageSize: 10 }}
            />
          </>
        ) : null}
      </Space>
    </Card>
  );
}
