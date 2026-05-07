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

interface BrokenImageDetectorInput {
  sourceDir: string;
  recursive: boolean;
  limit: number;
}

interface BrokenImageItem {
  path: string;
  name: string;
  extension: string;
  size: number;
  status: "broken" | "unsupported" | "failed";
  reason: string;
  modifiedAt: string | null;
}

interface BrokenImageDetectorData {
  sourceDir: string;
  recursive: boolean;
  totalFileCount: number;
  imageFileCount: number;
  normalImageCount: number;
  brokenImageCount: number;
  unsupportedImageCount: number;
  failedCount: number;
  limit: number;
  items: BrokenImageItem[];
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

function renderStatus(status: BrokenImageItem["status"]) {
  if (status === "broken") {
    return <Tag color="red">损坏</Tag>;
  }

  if (status === "unsupported") {
    return <Tag color="orange">不支持</Tag>;
  }

  return <Tag color="volcano">读取失败</Tag>;
}

const brokenImageColumns: ColumnsType<BrokenImageItem> = [
  {
    title: "文件名",
    dataIndex: "name",
    key: "name",
    width: 220,
    ellipsis: true,
  },
  {
    title: "类型",
    dataIndex: "extension",
    key: "extension",
    width: 100,
    render: (extension: string) => <Tag color="blue">{extension || "-"}</Tag>,
  },
  {
    title: "状态",
    dataIndex: "status",
    key: "status",
    width: 120,
    render: renderStatus,
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
    title: "原因",
    dataIndex: "reason",
    key: "reason",
    width: 260,
    ellipsis: true,
  },
  {
    title: "文件路径",
    dataIndex: "path",
    key: "path",
    ellipsis: true,
  },
];

export function BrokenImageDetectorPage() {
  const [sourceDir, setSourceDir] = useState("");
  const [recursive, setRecursive] = useState(true);
  const [limit, setLimit] = useState(500);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BrokenImageDetectorData | null>(null);

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
        BrokenImageDetectorInput,
        BrokenImageDetectorData
      >({
        pluginId: "broken-image-detector",
        input: {
          sourceDir,
          recursive,
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
      title="图片损坏检测"
      description="扫描指定目录下无法正常读取或解码的损坏图片文件。"
      warning={{
        message: "该功能只读取图片信息，不会修改文件",
        description:
          "检测结果只代表当前解码库是否能正常读取该图片。部分特殊格式可能会被识别为不支持。",
      }}
      result={result ? <BrokenImageDetectorResult result={result} /> : null}
    >
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <ToolPathPicker
          label="目标文件夹"
          value={sourceDir}
          placeholder="请选择需要检测损坏图片的文件夹"
          onSelect={handleSelectFolder}
        />

        <Divider style={{ margin: "12px 0" }} />

        <Space wrap>
          <Text strong>扫描选项</Text>

          <Text>递归扫描子文件夹</Text>
          <Switch checked={recursive} onChange={setRecursive} />

          <Text>最多展示异常图片数量</Text>
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
          开始检测
        </Button>
      </Space>
    </ToolPageLayout>
  );
}

interface BrokenImageDetectorResultProps {
  result: BrokenImageDetectorData;
}

function BrokenImageDetectorResult(props: BrokenImageDetectorResultProps) {
  const { result } = props;

  return (
    <Card title="检测结果">
      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <Space wrap size={16}>
          <Card size="small">
            <Statistic title="扫描文件数" value={result.totalFileCount} />
          </Card>

          <Card size="small">
            <Statistic title="图片文件数" value={result.imageFileCount} />
          </Card>

          <Card size="small">
            <Statistic title="正常图片数" value={result.normalImageCount} />
          </Card>

          <Card size="small">
            <Statistic title="损坏图片数" value={result.brokenImageCount} />
          </Card>

          <Card size="small">
            <Statistic
              title="不支持格式数"
              value={result.unsupportedImageCount}
            />
          </Card>
        </Space>

        <Descriptions bordered column={2} size="middle">
          <Descriptions.Item label="文件夹路径" span={2}>
            {result.sourceDir}
          </Descriptions.Item>

          <Descriptions.Item label="递归扫描">
            {result.recursive ? "是" : "否"}
          </Descriptions.Item>

          <Descriptions.Item label="扫描文件数">
            {result.totalFileCount}
          </Descriptions.Item>

          <Descriptions.Item label="图片文件数">
            {result.imageFileCount}
          </Descriptions.Item>

          <Descriptions.Item label="正常图片数">
            {result.normalImageCount}
          </Descriptions.Item>

          <Descriptions.Item label="损坏图片数">
            {result.brokenImageCount}
          </Descriptions.Item>

          <Descriptions.Item label="不支持格式数">
            {result.unsupportedImageCount}
          </Descriptions.Item>

          <Descriptions.Item label="读取失败数量">
            {result.failedCount}
          </Descriptions.Item>

          <Descriptions.Item label="最多展示数量">
            {result.limit}
          </Descriptions.Item>
        </Descriptions>

        {result.items.length > 0 ? (
          <>
            <Divider />

            <Table
              rowKey="path"
              size="small"
              columns={brokenImageColumns}
              dataSource={result.items}
              pagination={{ pageSize: 20 }}
            />
          </>
        ) : null}
      </Space>
    </Card>
  );
}
