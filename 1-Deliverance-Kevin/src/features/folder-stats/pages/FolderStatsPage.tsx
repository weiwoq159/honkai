import { useState } from "react";
import {
  Button,
  Card,
  Descriptions,
  Divider,
  Space,
  Statistic,
  message,
} from "antd";
import { SearchOutlined } from "@ant-design/icons";
import { selectFolder } from "@services/utils";
import { runTool } from "@services/toolRunner";
import { ToolPageLayout } from "@components/ToolPageLayout";
import { ToolPathPicker } from "@components/ToolPathPicker";

interface FolderStatsInput {
  sourceDir: string;
}

interface FolderStatsData {
  sourceDir: string;
  totalSize: number;
  totalFileCount: number;
  totalFolderCount: number;
  imageCount: number;
  videoCount: number;
  otherFileCount: number;
  createdAt: string | null;
  modifiedAt: string | null;
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

export function FolderStatsPage() {
  const [sourceDir, setSourceDir] = useState("");
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<FolderStatsData | null>(null);

  async function handleSelectFolder() {
    const selected = await selectFolder();

    if (!selected) {
      return;
    }

    setSourceDir(selected);
    setStats(null);
  }

  async function handleGetStats() {
    if (!sourceDir) {
      message.warning("请先选择文件夹");
      return;
    }

    try {
      setLoading(true);
      setStats(null);

      const result = await runTool<FolderStatsInput, FolderStatsData>({
        pluginId: "folder-stats",
        input: {
          sourceDir,
        },
      });

      if (!result.success || !result.data) {
        message.error(result.message);
        return;
      }

      setStats(result.data);
      message.success(result.message);
    } catch (error) {
      console.error(error);
      message.error("执行失败，请查看控制台日志");
    } finally {
      setLoading(false);
    }
  }

  return (
    <ToolPageLayout
      title="文件夹详情"
      description="选择一个本地文件夹，统计文件夹大小、文件数量、图片数量、视频数量、创建时间和修改时间。"
      warning={{
        message: "该功能只读取文件夹信息，不会修改文件",
        description:
          "统计结果会递归扫描所选文件夹下的所有子目录。文件数量较多时可能需要等待一段时间。",
      }}
      result={stats ? <FolderStatsResult stats={stats} /> : null}
    >
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <ToolPathPicker
          label="目标文件夹"
          value={sourceDir}
          placeholder="请选择需要查看详情的文件夹"
          onSelect={handleSelectFolder}
        />

        <Divider style={{ margin: "12px 0" }} />

        <Button
          type="primary"
          icon={<SearchOutlined />}
          loading={loading}
          disabled={!sourceDir}
          onClick={handleGetStats}
        >
          获取文件夹详情
        </Button>
      </Space>
    </ToolPageLayout>
  );
}

interface FolderStatsResultProps {
  stats: FolderStatsData;
}

function FolderStatsResult(props: FolderStatsResultProps) {
  const { stats } = props;

  return (
    <Card title="统计结果">
      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <Space wrap size={16}>
          <Card size="small">
            <Statistic
              title="文件夹大小"
              value={formatBytes(stats.totalSize)}
            />
          </Card>

          <Card size="small">
            <Statistic title="文件总数" value={stats.totalFileCount} />
          </Card>

          <Card size="small">
            <Statistic title="文件夹数量" value={stats.totalFolderCount} />
          </Card>

          <Card size="small">
            <Statistic title="图片数量" value={stats.imageCount} />
          </Card>

          <Card size="small">
            <Statistic title="视频数量" value={stats.videoCount} />
          </Card>
        </Space>

        <Descriptions bordered column={2} size="middle">
          <Descriptions.Item label="文件夹路径" span={2}>
            {stats.sourceDir}
          </Descriptions.Item>

          <Descriptions.Item label="文件夹大小">
            {formatBytes(stats.totalSize)}
          </Descriptions.Item>

          <Descriptions.Item label="文件总数">
            {stats.totalFileCount}
          </Descriptions.Item>

          <Descriptions.Item label="文件夹数量">
            {stats.totalFolderCount}
          </Descriptions.Item>

          <Descriptions.Item label="图片数量">
            {stats.imageCount}
          </Descriptions.Item>

          <Descriptions.Item label="视频数量">
            {stats.videoCount}
          </Descriptions.Item>

          <Descriptions.Item label="其他文件数量">
            {stats.otherFileCount}
          </Descriptions.Item>

          <Descriptions.Item label="读取失败数量">
            {stats.failedCount ?? 0}
          </Descriptions.Item>

          <Descriptions.Item label="创建时间">
            {stats.createdAt || "-"}
          </Descriptions.Item>

          <Descriptions.Item label="修改时间">
            {stats.modifiedAt || "-"}
          </Descriptions.Item>
        </Descriptions>
      </Space>
    </Card>
  );
}
