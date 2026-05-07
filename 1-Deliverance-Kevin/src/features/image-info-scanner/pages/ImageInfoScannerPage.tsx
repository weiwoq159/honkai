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

interface ImageInfoScannerInput {
  sourceDir: string;
  limit: number;
}

interface ImageInfoItem {
  path: string;
  name: string;
  extension: string;
  format: string;
  width: number;
  height: number;
  size: number;
  modifiedAt: string | null;
}

interface ImageInfoScannerData {
  sourceDir: string;
  totalFileCount: number;
  imageCount: number;
  totalImageSize: number;
  limit: number;
  items: ImageInfoItem[];
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

const imageInfoColumns: ColumnsType<ImageInfoItem> = [
  {
    title: "文件名",
    dataIndex: "name",
    key: "name",
    width: 220,
    ellipsis: true,
  },
  {
    title: "格式",
    dataIndex: "format",
    key: "format",
    width: 100,
    render: (format: string) => <Tag color="blue">{format || "-"}</Tag>,
  },
  {
    title: "尺寸",
    key: "dimension",
    width: 140,
    render: (_, record) => `${record.width} × ${record.height}`,
  },
  {
    title: "宽度",
    dataIndex: "width",
    key: "width",
    width: 100,
    sorter: (a, b) => a.width - b.width,
  },
  {
    title: "高度",
    dataIndex: "height",
    key: "height",
    width: 100,
    sorter: (a, b) => a.height - b.height,
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
  {
    title: "文件路径",
    dataIndex: "path",
    key: "path",
    ellipsis: true,
  },
];

export function ImageInfoScannerPage() {
  const [sourceDir, setSourceDir] = useState("");
  const [limit, setLimit] = useState(500);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ImageInfoScannerData | null>(null);

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
        ImageInfoScannerInput,
        ImageInfoScannerData
      >({
        pluginId: "image-info-scanner",
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
      title="图片基础信息扫描"
      description="扫描指定目录下的图片基础信息，包括尺寸、格式、文件大小和修改时间。"
      warning={{
        message: "该功能只读取图片信息，不会修改文件",
        description:
          "扫描结果会列出可识别图片的尺寸和格式。图片数量较多时可能需要等待一段时间。",
      }}
      result={result ? <ImageInfoScannerResult result={result} /> : null}
    >
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <ToolPathPicker
          label="目标文件夹"
          value={sourceDir}
          placeholder="请选择需要扫描图片信息的文件夹"
          onSelect={handleSelectFolder}
        />

        <Divider style={{ margin: "12px 0" }} />

        <Space wrap>
          <Text strong>扫描选项</Text>

          <Text>最多展示图片数量</Text>
          <InputNumber
            min={1}
            max={100000}
            value={limit}
            onChange={(value) => setLimit(value ?? 500)}
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

interface ImageInfoScannerResultProps {
  result: ImageInfoScannerData;
}

function ImageInfoScannerResult(props: ImageInfoScannerResultProps) {
  const { result } = props;

  return (
    <Card title="扫描结果">
      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <Space wrap size={16}>
          <Card size="small">
            <Statistic title="扫描文件数" value={result.totalFileCount} />
          </Card>

          <Card size="small">
            <Statistic title="图片数量" value={result.imageCount} />
          </Card>

          <Card size="small">
            <Statistic
              title="图片总大小"
              value={formatBytes(result.totalImageSize)}
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

          <Descriptions.Item label="图片数量">
            {result.imageCount}
          </Descriptions.Item>

          <Descriptions.Item label="图片总大小">
            {formatBytes(result.totalImageSize)}
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
              rowKey="path"
              size="small"
              columns={imageInfoColumns}
              dataSource={result.items}
              pagination={{ pageSize: 20 }}
            />
          </>
        ) : null}
      </Space>
    </Card>
  );
}
