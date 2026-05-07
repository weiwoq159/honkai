import { useState } from "react";
import {
  Button,
  Card,
  Descriptions,
  Divider,
  InputNumber,
  Space,
  Statistic,
  Switch,
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

interface DuplicateFilenameScannerInput {
  sourceDir: string;
  caseSensitive: boolean;
  limit: number;
}

interface DuplicateFilenameFileItem {
  path: string;
  size: number;
  modifiedAt: string | null;
}

interface DuplicateFilenameGroup {
  filename: string;
  count: number;
  totalSize: number;
  files: DuplicateFilenameFileItem[];
}

interface DuplicateFilenameScannerData {
  sourceDir: string;
  totalFileCount: number;
  duplicateNameCount: number;
  duplicateFileCount: number;
  duplicateTotalSize: number;
  caseSensitive: boolean;
  limit: number;
  groups: DuplicateFilenameGroup[];
  failedCount?: number;
  failedItems?: Array<{
    path: string;
    reason: string;
  }>;
}

interface DuplicateFilenameRow {
  key: string;
  filename: string;
  count: number;
  totalSize: number;
  path: string;
  size: number;
  modifiedAt: string | null;
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

function buildRows(groups: DuplicateFilenameGroup[]): DuplicateFilenameRow[] {
  return groups.flatMap((group) =>
    group.files.map((file, index) => ({
      key: `${group.filename}-${file.path}`,
      filename: index === 0 ? group.filename : "",
      count: index === 0 ? group.count : 0,
      totalSize: index === 0 ? group.totalSize : 0,
      path: file.path,
      size: file.size,
      modifiedAt: file.modifiedAt,
    })),
  );
}

const duplicateFilenameColumns: ColumnsType<DuplicateFilenameRow> = [
  {
    title: "重复文件名",
    dataIndex: "filename",
    key: "filename",
    width: 240,
    ellipsis: true,
    render: (filename: string, row) => {
      if (!filename) {
        return null;
      }

      return (
        <Space>
          <Tag color="blue">{filename}</Tag>
          <Text type="secondary">{row.count} 个</Text>
        </Space>
      );
    },
  },
  {
    title: "文件路径",
    dataIndex: "path",
    key: "path",
    ellipsis: true,
  },
  {
    title: "文件大小",
    dataIndex: "size",
    key: "size",
    width: 140,
    sorter: (a, b) => a.size - b.size,
    render: (size: number) => formatBytes(size),
  },
  {
    title: "修改时间",
    dataIndex: "modifiedAt",
    key: "modifiedAt",
    width: 180,
    render: (modifiedAt: string | null) => modifiedAt || "-",
  },
];

export function DuplicateFilenameScannerPage() {
  const [sourceDir, setSourceDir] = useState("");
  const [caseSensitive, setCaseSensitive] = useState(false);
  const [limit, setLimit] = useState(100);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DuplicateFilenameScannerData | null>(
    null,
  );

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
        DuplicateFilenameScannerInput,
        DuplicateFilenameScannerData
      >({
        pluginId: "duplicate-filename-scanner",
        input: {
          sourceDir,
          caseSensitive,
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
      title="重复文件名扫描"
      description="扫描指定目录下的重复文件名，帮助定位不同目录中的同名文件。"
      warning={{
        message: "该功能只读取文件信息，不会修改文件",
        description:
          "这里只比较文件名是否重复，不判断文件内容是否相同。如果要判断内容重复，后面应单独做文件哈希扫描。",
      }}
      result={
        result ? <DuplicateFilenameScannerResult result={result} /> : null
      }
    >
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <ToolPathPicker
          label="目标文件夹"
          value={sourceDir}
          placeholder="请选择需要扫描重复文件名的文件夹"
          onSelect={handleSelectFolder}
        />

        <Divider style={{ margin: "12px 0" }} />

        <Space wrap>
          <Text strong>扫描选项</Text>

          <Text>区分大小写</Text>
          <Switch checked={caseSensitive} onChange={setCaseSensitive} />

          <Text>最多展示组数</Text>
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

interface DuplicateFilenameScannerResultProps {
  result: DuplicateFilenameScannerData;
}

function DuplicateFilenameScannerResult(
  props: DuplicateFilenameScannerResultProps,
) {
  const { result } = props;
  const rows = buildRows(result.groups);

  return (
    <Card title="扫描结果">
      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <Space wrap size={16}>
          <Card size="small">
            <Statistic title="扫描文件数" value={result.totalFileCount} />
          </Card>

          <Card size="small">
            <Statistic title="重复文件名数" value={result.duplicateNameCount} />
          </Card>

          <Card size="small">
            <Statistic title="涉及文件数" value={result.duplicateFileCount} />
          </Card>

          <Card size="small">
            <Statistic
              title="涉及文件总大小"
              value={formatBytes(result.duplicateTotalSize)}
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

          <Descriptions.Item label="扫描文件数">
            {result.totalFileCount}
          </Descriptions.Item>

          <Descriptions.Item label="重复文件名数">
            {result.duplicateNameCount}
          </Descriptions.Item>

          <Descriptions.Item label="涉及文件数">
            {result.duplicateFileCount}
          </Descriptions.Item>

          <Descriptions.Item label="涉及文件总大小">
            {formatBytes(result.duplicateTotalSize)}
          </Descriptions.Item>

          <Descriptions.Item label="区分大小写">
            {result.caseSensitive ? "是" : "否"}
          </Descriptions.Item>

          <Descriptions.Item label="最多展示组数">
            {result.limit}
          </Descriptions.Item>

          <Descriptions.Item label="读取失败数量">
            {result.failedCount ?? 0}
          </Descriptions.Item>
        </Descriptions>

        {rows.length > 0 ? (
          <>
            <Divider />

            <Table
              rowKey="key"
              size="small"
              columns={duplicateFilenameColumns}
              dataSource={rows}
              pagination={{ pageSize: 20 }}
            />
          </>
        ) : null}
      </Space>
    </Card>
  );
}
