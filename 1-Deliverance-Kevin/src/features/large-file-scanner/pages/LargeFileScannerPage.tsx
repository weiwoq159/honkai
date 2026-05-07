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

interface LargeFileScannerInput {
  sourceDir: string;
  minSizeMb: number;
  limit: number;
}

interface LargeFileItem {
  path: string;
  name: string;
  size: number;
  sizeMb: number;
  modifiedAt: string | null;
}

interface LargeFileScannerData {
  sourceDir: string;
  minSizeMb: number;
  totalFileCount: number;
  matchedFileCount: number;
  totalMatchedSize: number;
  files: LargeFileItem[];
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

const largeFileColumns: ColumnsType<LargeFileItem> = [
  {
    title: "文件名",
    dataIndex: "name",
    key: "name",
    width: 220,
    ellipsis: true,
  },
  {
    title: "文件路径",
    dataIndex: "path",
    key: "path",
    ellipsis: true,
  },
  {
    title: "大小",
    dataIndex: "size",
    key: "size",
    width: 140,
    sorter: (a, b) => a.size - b.size,
    defaultSortOrder: "descend",
    render: (size: number) => <Tag color="red">{formatBytes(size)}</Tag>,
  },
  {
    title: "修改时间",
    dataIndex: "modifiedAt",
    key: "modifiedAt",
    width: 180,
    render: (modifiedAt: string | null) => modifiedAt || "-",
  },
];

export function LargeFileScannerPage() {
  const [sourceDir, setSourceDir] = useState("");
  const [minSizeMb, setMinSizeMb] = useState(100);
  const [limit, setLimit] = useState(100);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<LargeFileScannerData | null>(null);

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

      const response = await runTool<
        LargeFileScannerInput,
        LargeFileScannerData
      >({
        pluginId: "large-file-scanner",
        input: {
          sourceDir,
          minSizeMb,
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
      title="大文件扫描"
      description="选择一个本地文件夹，扫描指定大小以上的大文件，帮助定位占用空间较大的文件。"
      warning={{
        message: "该功能只读取文件信息，不会修改文件",
        description:
          "扫描结果会按文件大小倒序展示。文件数量较多时可能需要等待一段时间。",
      }}
      result={result ? <LargeFileScannerResult result={result} /> : null}
    >
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <ToolPathPicker
          label="目标文件夹"
          value={sourceDir}
          placeholder="请选择需要扫描大文件的文件夹"
          onSelect={handleSelectFolder}
        />

        <Divider style={{ margin: "12px 0" }} />

        <Space wrap>
          <Text strong>扫描选项</Text>

          <Text>最小文件大小 MB</Text>
          <InputNumber
            min={1}
            max={1024 * 1024}
            value={minSizeMb}
            onChange={(value) => setMinSizeMb(value ?? 100)}
          />

          <Text>最多展示数量</Text>
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
          开始扫描
        </Button>
      </Space>
    </ToolPageLayout>
  );
}

interface LargeFileScannerResultProps {
  result: LargeFileScannerData;
}

function LargeFileScannerResult(props: LargeFileScannerResultProps) {
  const { result } = props;

  return (
    <Card title="扫描结果">
      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <Space wrap size={16}>
          <Card size="small">
            <Statistic title="扫描文件数" value={result.totalFileCount} />
          </Card>

          <Card size="small">
            <Statistic title="命中文件数" value={result.matchedFileCount} />
          </Card>

          <Card size="small">
            <Statistic
              title="命中文件总大小"
              value={formatBytes(result.totalMatchedSize)}
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

          <Descriptions.Item label="最小文件大小">
            {result.minSizeMb} MB
          </Descriptions.Item>

          <Descriptions.Item label="扫描文件数">
            {result.totalFileCount}
          </Descriptions.Item>

          <Descriptions.Item label="命中文件数">
            {result.matchedFileCount}
          </Descriptions.Item>

          <Descriptions.Item label="命中文件总大小">
            {formatBytes(result.totalMatchedSize)}
          </Descriptions.Item>

          <Descriptions.Item label="读取失败数量">
            {result.failedCount ?? 0}
          </Descriptions.Item>
        </Descriptions>

        {result.files.length > 0 ? (
          <>
            <Divider />

            <Table
              rowKey="path"
              size="small"
              columns={largeFileColumns}
              dataSource={result.files}
              pagination={{ pageSize: 10 }}
            />
          </>
        ) : null}
      </Space>
    </Card>
  );
}
