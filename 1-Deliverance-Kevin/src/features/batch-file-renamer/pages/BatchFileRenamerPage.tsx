import { useState } from "react";
import {
  Button,
  Card,
  Descriptions,
  Divider,
  Input,
  InputNumber,
  Radio,
  Space,
  Statistic,
  Switch,
  Table,
  Tag,
  Typography,
  message,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import { EditOutlined } from "@ant-design/icons";
import { selectFolder } from "@services/utils";
import { runTool } from "@services/toolRunner";
import { ToolPageLayout } from "@components/ToolPageLayout";
import { ToolPathPicker } from "@components/ToolPathPicker";

const { Text } = Typography;

type RenameMode = "prefix" | "suffix" | "replace" | "sequence";

interface BatchFileRenamerInput {
  sourceDir: string;
  dryRun: boolean;
  recursive: boolean;
  mode: RenameMode;
  prefix: string;
  suffix: string;
  searchText: string;
  replaceText: string;
  sequencePrefix: string;
  startIndex: number;
  padding: number;
  conflictStrategy: "rename" | "skip";
}

interface BatchFileRenamerItem {
  sourcePath: string;
  targetPath: string;
  oldName: string;
  newName: string;
  status: "renamed" | "skipped" | "failed";
  reason?: string;
}

interface BatchFileRenamerData {
  sourceDir: string;
  dryRun: boolean;
  recursive: boolean;
  mode: RenameMode;
  scannedFileCount: number;
  renamedFileCount: number;
  skippedFileCount: number;
  failedCount: number;
  items: BatchFileRenamerItem[];
}

function formatStatus(status: BatchFileRenamerItem["status"]) {
  if (status === "renamed") {
    return <Tag color="green">已重命名</Tag>;
  }

  if (status === "skipped") {
    return <Tag color="blue">已跳过</Tag>;
  }

  return <Tag color="red">失败</Tag>;
}

const batchFileRenamerColumns: ColumnsType<BatchFileRenamerItem> = [
  {
    title: "原文件名",
    dataIndex: "oldName",
    key: "oldName",
    width: 220,
    ellipsis: true,
  },
  {
    title: "新文件名",
    dataIndex: "newName",
    key: "newName",
    width: 220,
    ellipsis: true,
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

export function BatchFileRenamerPage() {
  const [sourceDir, setSourceDir] = useState("");
  const [dryRun, setDryRun] = useState(true);
  const [recursive, setRecursive] = useState(false);
  const [mode, setMode] = useState<RenameMode>("prefix");

  const [prefix, setPrefix] = useState("new_");
  const [suffix, setSuffix] = useState("_new");
  const [searchText, setSearchText] = useState("");
  const [replaceText, setReplaceText] = useState("");
  const [sequencePrefix, setSequencePrefix] = useState("file_");
  const [startIndex, setStartIndex] = useState(1);
  const [padding, setPadding] = useState(3);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BatchFileRenamerData | null>(null);

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

    if (mode === "replace" && !searchText) {
      message.warning("替换模式下，查找内容不能为空");
      return;
    }

    if (mode === "prefix" && !prefix) {
      message.warning("前缀不能为空");
      return;
    }

    if (mode === "suffix" && !suffix) {
      message.warning("后缀不能为空");
      return;
    }

    if (mode === "sequence" && !sequencePrefix) {
      message.warning("序号前缀不能为空");
      return;
    }

    try {
      setLoading(true);
      setResult(null);

      const response = await runTool<
        BatchFileRenamerInput,
        BatchFileRenamerData
      >({
        pluginId: "batch-file-renamer",
        input: {
          sourceDir,
          dryRun,
          recursive,
          mode,
          prefix,
          suffix,
          searchText,
          replaceText,
          sequencePrefix,
          startIndex,
          padding,
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
      setLoading(false);
    }
  }

  return (
    <ToolPageLayout
      title="批量重命名"
      description="按指定规则批量重命名文件，支持添加前缀、添加后缀、文本替换和序号命名。"
      warning={{
        message: "该操作会修改文件名",
        description:
          "建议先开启预览模式确认重命名结果。确认无误后再关闭预览模式执行实际重命名。",
      }}
      result={result ? <BatchFileRenamerResult result={result} /> : null}
    >
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <ToolPathPicker
          label="目标文件夹"
          value={sourceDir}
          placeholder="请选择需要批量重命名的文件夹"
          onSelect={handleSelectFolder}
        />

        <Divider style={{ margin: "12px 0" }} />

        <Space direction="vertical" size={8}>
          <Text strong>执行选项</Text>

          <Space>
            <Switch checked={dryRun} onChange={setDryRun} />
            <Text>仅预览，不实际重命名</Text>
            <Tag color="orange">安全模式</Tag>
          </Space>

          <Space>
            <Switch checked={recursive} onChange={setRecursive} />
            <Text>递归处理子文件夹中的文件</Text>
          </Space>

          <Space>
            <Switch checked disabled />
            <Text>文件名冲突时自动重命名</Text>
            <Tag color="blue">推荐</Tag>
          </Space>
        </Space>

        <Divider style={{ margin: "12px 0" }} />

        <Space direction="vertical" size={12} style={{ width: "100%" }}>
          <Text strong>重命名规则</Text>

          <Radio.Group
            value={mode}
            onChange={(event) => setMode(event.target.value)}
            optionType="button"
            buttonStyle="solid"
            options={[
              {
                label: "添加前缀",
                value: "prefix",
              },
              {
                label: "添加后缀",
                value: "suffix",
              },
              {
                label: "文本替换",
                value: "replace",
              },
              {
                label: "序号命名",
                value: "sequence",
              },
            ]}
          />

          {mode === "prefix" ? (
            <Space>
              <Text>前缀</Text>
              <Input
                style={{ width: 260 }}
                value={prefix}
                onChange={(event) => setPrefix(event.target.value)}
              />
            </Space>
          ) : null}

          {mode === "suffix" ? (
            <Space>
              <Text>后缀</Text>
              <Input
                style={{ width: 260 }}
                value={suffix}
                onChange={(event) => setSuffix(event.target.value)}
              />
            </Space>
          ) : null}

          {mode === "replace" ? (
            <Space>
              <Text>查找</Text>
              <Input
                style={{ width: 220 }}
                value={searchText}
                onChange={(event) => setSearchText(event.target.value)}
              />

              <Text>替换为</Text>
              <Input
                style={{ width: 220 }}
                value={replaceText}
                onChange={(event) => setReplaceText(event.target.value)}
              />
            </Space>
          ) : null}

          {mode === "sequence" ? (
            <Space wrap>
              <Text>序号前缀</Text>
              <Input
                style={{ width: 220 }}
                value={sequencePrefix}
                onChange={(event) => setSequencePrefix(event.target.value)}
              />

              <Text>起始序号</Text>
              <InputNumber
                min={0}
                max={999999}
                value={startIndex}
                onChange={(value) => setStartIndex(value ?? 1)}
              />

              <Text>补零位数</Text>
              <InputNumber
                min={1}
                max={12}
                value={padding}
                onChange={(value) => setPadding(value ?? 3)}
              />
            </Space>
          ) : null}
        </Space>

        <Divider style={{ margin: "12px 0" }} />

        <Button
          type="primary"
          danger={!dryRun}
          icon={<EditOutlined />}
          loading={loading}
          disabled={!sourceDir}
          onClick={handleRun}
        >
          {dryRun ? "预览重命名结果" : "开始重命名"}
        </Button>
      </Space>
    </ToolPageLayout>
  );
}

interface BatchFileRenamerResultProps {
  result: BatchFileRenamerData;
}

function BatchFileRenamerResult(props: BatchFileRenamerResultProps) {
  const { result } = props;

  return (
    <Card title={result.dryRun ? "预览结果" : "重命名结果"}>
      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <Space wrap size={16}>
          <Card size="small">
            <Statistic title="扫描文件数" value={result.scannedFileCount} />
          </Card>

          <Card size="small">
            <Statistic title="重命名文件数" value={result.renamedFileCount} />
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
              <Tag color="red">实际重命名</Tag>
            )}
          </Descriptions.Item>

          <Descriptions.Item label="递归处理">
            {result.recursive ? "是" : "否"}
          </Descriptions.Item>

          <Descriptions.Item label="重命名模式">
            {result.mode}
          </Descriptions.Item>

          <Descriptions.Item label="扫描文件数">
            {result.scannedFileCount}
          </Descriptions.Item>

          <Descriptions.Item label="重命名文件数">
            {result.renamedFileCount}
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
              columns={batchFileRenamerColumns}
              dataSource={result.items}
              pagination={{ pageSize: 10 }}
            />
          </>
        ) : null}
      </Space>
    </Card>
  );
}
