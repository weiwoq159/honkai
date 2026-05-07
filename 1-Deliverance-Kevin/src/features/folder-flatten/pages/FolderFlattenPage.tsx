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
import { PlayCircleOutlined } from "@ant-design/icons";
import { selectFolder } from "@services/utils";
import { runTool } from "@services/toolRunner";
import { ToolPageLayout } from "@components/ToolPageLayout";
import { ToolPathPicker } from "@components/ToolPathPicker";

const { Text } = Typography;

interface FolderFlattenInput {
  sourceDir: string;
  removeEmptyDirs?: boolean;
  conflictStrategy?: "rename" | "skip";
}

interface FailedFile {
  path: string;
  reason: string;
}

interface FolderFlattenData {
  sourceDir: string;
  movedCount: number;
  skippedCount: number;
  conflictRenamedCount: number;
  removedEmptyDirCount: number;
  failedCount: number;
  failedFiles: FailedFile[];
}

const failedFileColumns: ColumnsType<FailedFile> = [
  {
    title: "文件路径",
    dataIndex: "path",
    key: "path",
    ellipsis: true,
  },
  {
    title: "失败原因",
    dataIndex: "reason",
    key: "reason",
    width: 240,
  },
];

export function FolderFlattenPage() {
  const [sourceDir, setSourceDir] = useState("");
  const [removeEmptyDirs, setRemoveEmptyDirs] = useState(true);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<FolderFlattenData | null>(null);

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

      const response = await runTool<FolderFlattenInput, FolderFlattenData>({
        pluginId: "folder-flatten",
        input: {
          sourceDir,
          removeEmptyDirs,
          conflictStrategy: "rename",
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
      title="文件夹拉平"
      description={
        <>
          将所选文件夹下的多层级文件移动到当前文件夹根目录。根目录已有文件不会移动；
          如果出现同名文件，会自动重命名，避免覆盖原文件。
        </>
      }
      warning={{
        message: "执行前请确认文件夹路径",
        description:
          "该操作会移动文件位置。建议先在测试文件夹中验证，或确保重要文件已有备份。",
      }}
      result={result ? <FolderFlattenResult result={result} /> : null}
    >
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <ToolPathPicker
          label="目标文件夹"
          value={sourceDir}
          placeholder="请选择需要拉平的文件夹"
          onSelect={handleSelectFolder}
        />

        <Divider style={{ margin: "12px 0" }} />

        <Space direction="vertical" size={8}>
          <Text strong>执行选项</Text>

          <Space>
            <Switch checked disabled />
            <Text>文件名冲突时自动重命名</Text>
            <Tag color="blue">推荐</Tag>
          </Space>

          <Space>
            <Switch checked={removeEmptyDirs} onChange={setRemoveEmptyDirs} />
            <Text>拉平后删除空文件夹</Text>
          </Space>

          <Space>
            <Switch checked disabled />
            <Text>跳过根目录已有文件</Text>
          </Space>
        </Space>

        <Divider style={{ margin: "12px 0" }} />

        <Button
          type="primary"
          icon={<PlayCircleOutlined />}
          loading={running}
          disabled={!sourceDir}
          onClick={handleRun}
        >
          开始拉平
        </Button>
      </Space>
    </ToolPageLayout>
  );
}

interface FolderFlattenResultProps {
  result: FolderFlattenData;
}

function FolderFlattenResult(props: FolderFlattenResultProps) {
  const { result } = props;

  return (
    <Card title="执行结果">
      <Descriptions bordered column={2} size="middle">
        <Descriptions.Item label="源文件夹" span={2}>
          {result.sourceDir}
        </Descriptions.Item>

        <Descriptions.Item label="移动文件数">
          {result.movedCount}
        </Descriptions.Item>

        <Descriptions.Item label="跳过文件数">
          {result.skippedCount}
        </Descriptions.Item>

        <Descriptions.Item label="重命名文件数">
          {result.conflictRenamedCount}
        </Descriptions.Item>

        <Descriptions.Item label="删除空文件夹数">
          {result.removedEmptyDirCount}
        </Descriptions.Item>

        <Descriptions.Item label="失败数量">
          {result.failedCount}
        </Descriptions.Item>
      </Descriptions>

      {result.failedFiles.length > 0 ? (
        <>
          <Divider />

          <Table
            rowKey="path"
            size="small"
            columns={failedFileColumns}
            dataSource={result.failedFiles}
            pagination={{ pageSize: 5 }}
          />
        </>
      ) : null}
    </Card>
  );
}
