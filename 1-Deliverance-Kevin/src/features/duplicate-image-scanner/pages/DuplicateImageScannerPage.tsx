import { useEffect, useMemo, useState } from "react";
import {
  Button,
  Card,
  Checkbox,
  Descriptions,
  Divider,
  Image,
  InputNumber,
  Modal,
  Progress,
  Space,
  Statistic,
  Switch,
  Tag,
  Typography,
  message,
} from "antd";
import { DeleteOutlined, SearchOutlined } from "@ant-design/icons";
import { convertFileSrc } from "@tauri-apps/api/core";
import { selectFolder } from "@services/utils";
import { listenToolProgress, runTool } from "@services/toolRunner";
import { moveFilesToTrash } from "@services/fileOps";
import { ToolPageLayout } from "@components/ToolPageLayout";
import { ToolPathPicker } from "@components/ToolPathPicker";

const { Text } = Typography;

const PLUGIN_ID = "duplicate-image-scanner";

interface DuplicateImageScannerInput {
  sourceDir: string;
  recursive: boolean;
  threshold: number;
  limit: number;
  maxFiles: number;
  maxImages: number;
  bucketPrefixLength: number;
  maxBucketSize: number;
}

interface PluginProgress {
  stage: string;
  current: number;
  total: number;
  percent: number;
  message: string;
}

interface DuplicateImageItem {
  path: string;
  name: string;
  size: number;
  width: number;
  height: number;
  format: string;
  hash: string;
  distance: number;
  qualityScore: number;
  recommendedKeep: boolean;
  recommendedDelete: boolean;
  modifiedAt: string | null;
}

interface DuplicateImageGroup {
  groupId: number;
  count: number;
  minDistance: number;
  maxDistance: number;
  files: DuplicateImageItem[];
}

interface DuplicateImageScannerData {
  sourceDir: string;
  recursive: boolean;
  threshold: number;
  totalFileCount: number;
  imageCount: number;
  duplicateGroupCount: number;
  duplicateImageCount: number;
  failedCount: number;
  skippedFileCount: number;
  maxFiles: number;
  maxImages: number;
  bucketPrefixLength: number;
  maxBucketSize: number;
  bucketCount: number;
  comparedPairCount: number;
  skippedBucketCount: number;
  limit: number;
  groups: DuplicateImageGroup[];
  failedItems: Array<{
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

function formatNumber(value: number | undefined | null): string {
  return typeof value === "number" ? value.toLocaleString() : "-";
}

function getRecommendedDeletePaths(result: DuplicateImageScannerData | null) {
  if (!result) return [];

  return result.groups.flatMap((group) =>
    group.files
      .filter((file) => file.recommendedDelete)
      .map((file) => file.path),
  );
}

export function DuplicateImageScannerPage() {
  const [sourceDir, setSourceDir] = useState("");
  const [recursive, setRecursive] = useState(true);
  const [threshold, setThreshold] = useState(5);
  const [limit, setLimit] = useState(100);

  const [maxFiles, setMaxFiles] = useState(5000);
  const [maxImages, setMaxImages] = useState(1000);
  const [bucketPrefixLength, setBucketPrefixLength] = useState(4);
  const [maxBucketSize, setMaxBucketSize] = useState(300);

  const [loading, setLoading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [progress, setProgress] = useState<PluginProgress | null>(null);
  const [result, setResult] = useState<DuplicateImageScannerData | null>(null);
  const [selectedPaths, setSelectedPaths] = useState<string[]>([]);

  const selectedPathSet = useMemo(
    () => new Set(selectedPaths),
    [selectedPaths],
  );

  const recommendedDeletePaths = useMemo(
    () => getRecommendedDeletePaths(result),
    [result],
  );

  useEffect(() => {
    let unlistenProgress: (() => void) | undefined;

    listenToolProgress<PluginProgress>((payload) => {
      if (payload.pluginId !== PLUGIN_ID) {
        return;
      }

      setProgress(payload.data);
    }).then((fn) => {
      unlistenProgress = fn;
    });

    return () => {
      unlistenProgress?.();
    };
  }, []);

  async function handleSelectFolder() {
    const selected = await selectFolder();

    if (!selected) {
      return;
    }

    setSourceDir(selected);
    setResult(null);
    setProgress(null);
    setSelectedPaths([]);
  }

  function handleTogglePath(path: string, checked: boolean) {
    setSelectedPaths((prev) => {
      if (checked) {
        return Array.from(new Set([...prev, path]));
      }

      return prev.filter((item) => item !== path);
    });
  }

  function handleSelectRecommendedDelete() {
    if (recommendedDeletePaths.length === 0) {
      message.info("当前没有推荐删除的图片");
      return;
    }

    setSelectedPaths(Array.from(new Set(recommendedDeletePaths)));
    message.success(`已选中 ${recommendedDeletePaths.length} 张推荐删除图片`);
  }

  function handleClearSelected() {
    setSelectedPaths([]);
  }

  async function handleScan() {
    if (!sourceDir) {
      message.warning("请先选择文件夹");
      return;
    }

    try {
      setLoading(true);
      setResult(null);
      setProgress(null);
      setSelectedPaths([]);

      const response = await runTool<
        DuplicateImageScannerInput,
        DuplicateImageScannerData
      >({
        pluginId: PLUGIN_ID,
        input: {
          sourceDir,
          recursive,
          threshold,
          limit,
          maxFiles,
          maxImages,
          bucketPrefixLength,
          maxBucketSize,
        },
      });

      if (!response.success || !response.data) {
        message.error(response.message);
        return;
      }

      setResult(response.data);
      setSelectedPaths(getRecommendedDeletePaths(response.data));
      message.success(response.message);
    } catch (error) {
      console.error(error);

      const errorMessage =
        error instanceof Error ? error.message : String(error);

      message.error(errorMessage || "执行失败，请查看控制台日志");
    } finally {
      setLoading(false);
    }
  }

  async function deleteSelectedFiles() {
    if (selectedPaths.length === 0) {
      message.warning("请先选择需要删除的图片");
      return;
    }

    try {
      setDeleting(true);

      const response = await moveFilesToTrash({
        filePaths: selectedPaths,
      });

      if (response.failedCount > 0) {
        message.warning(response.message);
      } else {
        message.success(response.message);
      }

      const deletedPathSet = new Set(
        response.items.filter((item) => item.success).map((item) => item.path),
      );

      setSelectedPaths((prev) =>
        prev.filter((path) => !deletedPathSet.has(path)),
      );

      setResult((prev) => {
        if (!prev) return prev;

        const nextGroups = prev.groups
          .map((group) => {
            const nextFiles = group.files.filter(
              (file) => !deletedPathSet.has(file.path),
            );

            return {
              ...group,
              count: nextFiles.length,
              files: nextFiles,
            };
          })
          .filter((group) => group.files.length > 1);

        const nextDuplicateImageCount = nextGroups.reduce(
          (sum, group) => sum + group.files.length,
          0,
        );

        return {
          ...prev,
          groups: nextGroups,
          duplicateGroupCount: nextGroups.length,
          duplicateImageCount: nextDuplicateImageCount,
        };
      });
    } catch (error) {
      console.error(error);

      const errorMessage =
        error instanceof Error ? error.message : String(error);

      message.error(errorMessage || "删除失败，请查看控制台日志");
    } finally {
      setDeleting(false);
    }
  }

  function handleDeleteSelected() {
    if (selectedPaths.length === 0) {
      message.warning("请先选择需要删除的图片");
      return;
    }

    Modal.confirm({
      title: "确认删除选中的图片？",
      content: `将 ${selectedPaths.length} 个文件移入系统回收站。该操作不会直接永久删除文件。`,
      okText: "移入回收站",
      cancelText: "取消",
      okButtonProps: {
        danger: true,
        loading: deleting,
      },
      async onOk() {
        await deleteSelectedFiles();
      },
    });
  }

  return (
    <ToolPageLayout
      title="图片重复扫描"
      description="扫描指定目录下的相似或重复图片，并按相似度分组展示。"
      warning={{
        message: "该功能只读取图片信息，删除时会移入系统回收站",
        description:
          "当前版本使用 pHash 感知哈希 + 分桶比较。扫描完成后会默认勾选推荐删除项，请手动确认后再删除。",
      }}
      result={
        result ? (
          <DuplicateImageScannerResult
            result={result}
            selectedPathSet={selectedPathSet}
            selectedCount={selectedPaths.length}
            recommendedDeleteCount={recommendedDeletePaths.length}
            deleting={deleting}
            onTogglePath={handleTogglePath}
            onSelectRecommendedDelete={handleSelectRecommendedDelete}
            onClearSelected={handleClearSelected}
            onDeleteSelected={handleDeleteSelected}
          />
        ) : null
      }
    >
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <ToolPathPicker
          label="目标文件夹"
          value={sourceDir}
          placeholder="请选择需要扫描重复图片的文件夹"
          onSelect={handleSelectFolder}
        />

        <Divider style={{ margin: "12px 0" }} />

        <Card size="small" title="基础扫描选项">
          <Space wrap>
            <Text>递归扫描子文件夹</Text>
            <Switch checked={recursive} onChange={setRecursive} />

            <Text>相似阈值</Text>
            <InputNumber
              min={0}
              max={20}
              value={threshold}
              onChange={(value) => setThreshold(value ?? 5)}
            />

            <Text>最多展示组数</Text>
            <InputNumber
              min={1}
              max={10000}
              value={limit}
              onChange={(value) => setLimit(value ?? 100)}
            />
          </Space>
        </Card>

        <Card size="small" title="性能限制">
          <Space wrap>
            <Text>最多扫描文件数</Text>
            <InputNumber
              min={100}
              max={200000}
              step={500}
              value={maxFiles}
              onChange={(value) => setMaxFiles(value ?? 5000)}
            />

            <Text>最多处理图片数</Text>
            <InputNumber
              min={100}
              max={50000}
              step={100}
              value={maxImages}
              onChange={(value) => setMaxImages(value ?? 1000)}
            />

            <Text>Hash 分桶前缀长度</Text>
            <InputNumber
              min={2}
              max={8}
              value={bucketPrefixLength}
              onChange={(value) => setBucketPrefixLength(value ?? 4)}
            />

            <Text>单桶最多比较图片数</Text>
            <InputNumber
              min={20}
              max={5000}
              step={50}
              value={maxBucketSize}
              onChange={(value) => setMaxBucketSize(value ?? 300)}
            />
          </Space>

          <Divider style={{ margin: "12px 0" }} />

          <Space direction="vertical" size={4}>
            <Text type="secondary">
              推荐默认值：maxFiles=5000，maxImages=1000，bucketPrefixLength=4，maxBucketSize=300。
            </Text>
            <Text type="secondary">
              如果漏图较多，把 Hash 分桶前缀长度调成 3；如果速度太慢，把它调成
              5。
            </Text>
          </Space>
        </Card>

        <Space wrap>
          <Button
            type="primary"
            icon={<SearchOutlined />}
            loading={loading}
            disabled={!sourceDir}
            onClick={handleScan}
          >
            开始扫描
          </Button>

          <Button
            danger
            icon={<DeleteOutlined />}
            disabled={selectedPaths.length === 0}
            loading={deleting}
            onClick={handleDeleteSelected}
          >
            删除选中图片（{selectedPaths.length}）
          </Button>

          <Button
            disabled={recommendedDeletePaths.length === 0}
            onClick={handleSelectRecommendedDelete}
          >
            选中推荐删除（{recommendedDeletePaths.length}）
          </Button>

          <Button
            disabled={selectedPaths.length === 0}
            onClick={handleClearSelected}
          >
            清空选择
          </Button>
        </Space>

        {progress ? <PluginProgressCard progress={progress} /> : null}
      </Space>
    </ToolPageLayout>
  );
}

interface PluginProgressCardProps {
  progress: PluginProgress;
}

function PluginProgressCard(props: PluginProgressCardProps) {
  const { progress } = props;

  return (
    <Card size="small">
      <Space direction="vertical" size={8} style={{ width: "100%" }}>
        <Space wrap>
          <Tag color="blue">{progress.stage}</Tag>
          <Text>{progress.message}</Text>
        </Space>

        <Progress percent={Math.round(progress.percent)} />

        <Text type="secondary">
          {formatNumber(progress.current)} / {formatNumber(progress.total)}
        </Text>
      </Space>
    </Card>
  );
}

interface DuplicateImageScannerResultProps {
  result: DuplicateImageScannerData;
  selectedPathSet: Set<string>;
  selectedCount: number;
  recommendedDeleteCount: number;
  deleting: boolean;
  onTogglePath: (path: string, checked: boolean) => void;
  onSelectRecommendedDelete: () => void;
  onClearSelected: () => void;
  onDeleteSelected: () => void;
}

function DuplicateImageScannerResult(props: DuplicateImageScannerResultProps) {
  const {
    result,
    selectedPathSet,
    selectedCount,
    recommendedDeleteCount,
    deleting,
    onTogglePath,
    onSelectRecommendedDelete,
    onClearSelected,
    onDeleteSelected,
  } = props;

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
            <Statistic title="重复组数" value={result.duplicateGroupCount} />
          </Card>

          <Card size="small">
            <Statistic title="涉及图片数" value={result.duplicateImageCount} />
          </Card>

          <Card size="small">
            <Statistic title="已选中" value={selectedCount} />
          </Card>

          <Card size="small">
            <Statistic title="推荐删除" value={recommendedDeleteCount} />
          </Card>

          <Card size="small">
            <Statistic title="实际比较次数" value={result.comparedPairCount} />
          </Card>

          <Card size="small">
            <Statistic title="分桶数量" value={result.bucketCount} />
          </Card>
        </Space>

        <Space wrap>
          <Button
            danger
            icon={<DeleteOutlined />}
            disabled={selectedCount === 0}
            loading={deleting}
            onClick={onDeleteSelected}
          >
            删除选中图片（{selectedCount}）
          </Button>

          <Button
            disabled={recommendedDeleteCount === 0}
            onClick={onSelectRecommendedDelete}
          >
            选中推荐删除（{recommendedDeleteCount}）
          </Button>

          <Button disabled={selectedCount === 0} onClick={onClearSelected}>
            清空选择
          </Button>
        </Space>

        <Descriptions bordered column={2} size="middle">
          <Descriptions.Item label="文件夹路径" span={2}>
            {result.sourceDir}
          </Descriptions.Item>

          <Descriptions.Item label="递归扫描">
            {result.recursive ? "是" : "否"}
          </Descriptions.Item>

          <Descriptions.Item label="相似阈值">
            {result.threshold}
          </Descriptions.Item>

          <Descriptions.Item label="最多扫描文件数">
            {formatNumber(result.maxFiles)}
          </Descriptions.Item>

          <Descriptions.Item label="最多处理图片数">
            {formatNumber(result.maxImages)}
          </Descriptions.Item>

          <Descriptions.Item label="Hash 分桶前缀长度">
            {result.bucketPrefixLength}
          </Descriptions.Item>

          <Descriptions.Item label="单桶最多比较图片数">
            {formatNumber(result.maxBucketSize)}
          </Descriptions.Item>

          <Descriptions.Item label="扫描文件数">
            {formatNumber(result.totalFileCount)}
          </Descriptions.Item>

          <Descriptions.Item label="图片数量">
            {formatNumber(result.imageCount)}
          </Descriptions.Item>

          <Descriptions.Item label="分桶数量">
            {formatNumber(result.bucketCount)}
          </Descriptions.Item>

          <Descriptions.Item label="实际比较次数">
            {formatNumber(result.comparedPairCount)}
          </Descriptions.Item>

          <Descriptions.Item label="跳过超大桶数量">
            {formatNumber(result.skippedBucketCount)}
          </Descriptions.Item>

          <Descriptions.Item label="跳过文件数量">
            {formatNumber(result.skippedFileCount)}
          </Descriptions.Item>

          <Descriptions.Item label="重复组数">
            {formatNumber(result.duplicateGroupCount)}
          </Descriptions.Item>

          <Descriptions.Item label="涉及图片数">
            {formatNumber(result.duplicateImageCount)}
          </Descriptions.Item>

          <Descriptions.Item label="读取失败数量">
            {formatNumber(result.failedCount)}
          </Descriptions.Item>

          <Descriptions.Item label="最多展示组数">
            {formatNumber(result.limit)}
          </Descriptions.Item>
        </Descriptions>

        {result.groups.length > 0 ? (
          <>
            <Divider />

            <Space direction="vertical" size={16} style={{ width: "100%" }}>
              {result.groups.map((group) => (
                <DuplicateImageGroupCard
                  key={group.groupId}
                  group={group}
                  selectedPathSet={selectedPathSet}
                  onTogglePath={onTogglePath}
                />
              ))}
            </Space>
          </>
        ) : (
          <Card size="small">
            <Text type="secondary">未发现重复或相似图片。</Text>
          </Card>
        )}

        {result.failedItems.length > 0 ? (
          <>
            <Divider />

            <Card size="small" title="读取失败文件">
              <Space direction="vertical" size={8} style={{ width: "100%" }}>
                {result.failedItems.slice(0, 20).map((item) => (
                  <Text key={item.path} type="secondary">
                    {item.path}：{item.reason}
                  </Text>
                ))}

                {result.failedItems.length > 20 ? (
                  <Text type="secondary">
                    还有 {result.failedItems.length - 20} 条失败记录未展示。
                  </Text>
                ) : null}
              </Space>
            </Card>
          </>
        ) : null}
      </Space>
    </Card>
  );
}

interface DuplicateImageGroupCardProps {
  group: DuplicateImageGroup;
  selectedPathSet: Set<string>;
  onTogglePath: (path: string, checked: boolean) => void;
}

function DuplicateImageGroupCard(props: DuplicateImageGroupCardProps) {
  const { group, selectedPathSet, onTogglePath } = props;

  const selectedInGroupCount = group.files.filter((file) =>
    selectedPathSet.has(file.path),
  ).length;

  return (
    <Card
      size="small"
      title={`重复组 #${group.groupId}`}
      extra={
        <Space>
          <Tag color="blue">{group.count} 张</Tag>
          <Tag color="cyan">已选 {selectedInGroupCount}</Tag>
          <Tag color="purple">
            距离 {group.minDistance} - {group.maxDistance}
          </Tag>
        </Space>
      }
    >
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
          gap: 12,
        }}
      >
        {group.files.map((item) => (
          <DuplicateImageItemCard
            key={item.path}
            item={item}
            checked={selectedPathSet.has(item.path)}
            onTogglePath={onTogglePath}
          />
        ))}
      </div>
    </Card>
  );
}

interface DuplicateImageItemCardProps {
  item: DuplicateImageItem;
  checked: boolean;
  onTogglePath: (path: string, checked: boolean) => void;
}

function DuplicateImageItemCard(props: DuplicateImageItemCardProps) {
  const { item, checked, onTogglePath } = props;

  const imageSrc = convertFileSrc(item.path);

  return (
    <Card
      size="small"
      styles={{
        body: {
          padding: 12,
          border: checked ? "1px solid #ff4d4f" : undefined,
          borderRadius: 8,
        },
      }}
    >
      <Space direction="vertical" size={8} style={{ width: "100%" }}>
        <Checkbox
          checked={checked}
          disabled={item.recommendedKeep}
          onChange={(event) => onTogglePath(item.path, event.target.checked)}
        >
          {item.recommendedKeep ? "推荐保留" : "选中删除"}
        </Checkbox>

        <Image
          src={imageSrc}
          width="100%"
          height={160}
          style={{
            objectFit: "cover",
            borderRadius: 8,
            background: "#f5f5f5",
          }}
          preview={{
            src: imageSrc,
          }}
        />

        <Space wrap>
          {item.recommendedKeep ? <Tag color="green">推荐保留</Tag> : null}
          {item.recommendedDelete ? <Tag color="orange">建议处理</Tag> : null}
          {checked ? <Tag color="red">待删除</Tag> : null}
          <Tag>{item.format}</Tag>
        </Space>

        <Text strong ellipsis={{ tooltip: item.name }}>
          {item.name}
        </Text>

        <Space direction="vertical" size={2} style={{ width: "100%" }}>
          <Text type="secondary">
            尺寸：{item.width} × {item.height}
          </Text>

          <Text type="secondary">大小：{formatBytes(item.size)}</Text>

          <Text type="secondary">距离：{item.distance}</Text>

          <Text type="secondary">质量分：{Math.round(item.qualityScore)}</Text>

          <Text type="secondary" ellipsis={{ tooltip: item.path }}>
            路径：{item.path}
          </Text>
        </Space>
      </Space>
    </Card>
  );
}
