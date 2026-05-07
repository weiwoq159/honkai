import { useMemo, useState } from "react";
import {
  Button,
  Card,
  Divider,
  Input,
  InputNumber,
  Radio,
  Space,
  Switch,
  Tree,
  Typography,
  message,
} from "antd";
import type { DataNode } from "antd/es/tree";
import { SearchOutlined } from "@ant-design/icons";
import { selectFolder } from "@services/utils";
import { runTool } from "@services/toolRunner";
import { ToolPageLayout } from "@components/ToolPageLayout";
import { ToolPathPicker } from "@components/ToolPathPicker";
import type { FolderTreeData, FolderTreeInput, FolderTreeNode } from "../types";

const { Text } = Typography;
const { TextArea } = Input;

type ViewMode = "markdown" | "tree";

function convertToTreeData(node: FolderTreeNode): DataNode {
  return {
    key: node.path,
    title: (
      <span>
        {node.type === "directory" ? "📁" : "📄"} {node.name || node.path}
        {node.truncated ? "（已截断）" : ""}
        {node.error ? `（${node.error}）` : ""}
      </span>
    ),
    children: node.children?.map(convertToTreeData),
  };
}

function convertToMarkdown(node: FolderTreeNode, depth = 0): string {
  const indent = "  ".repeat(depth);
  const icon = node.type === "directory" ? "📁" : "📄";
  const name = node.name || node.path;
  const suffix = [
    node.truncated ? "（已截断）" : "",
    node.error ? `（${node.error}）` : "",
  ].join("");

  const currentLine = `${indent}- ${icon} ${name}${suffix}`;
  const children = node.children ?? [];

  if (children.length === 0) {
    return currentLine;
  }

  return [
    currentLine,
    ...children.map((child) => convertToMarkdown(child, depth + 1)),
  ].join("\n");
}

export function FolderTreePage() {
  const [sourceDir, setSourceDir] = useState("");
  const [maxDepth, setMaxDepth] = useState(5);
  const [includeFiles, setIncludeFiles] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>("markdown");
  const [treeData, setTreeData] = useState<DataNode[]>([]);
  const [summary, setSummary] = useState<FolderTreeData | null>(null);
  const [loading, setLoading] = useState(false);

  const markdownText = useMemo(() => {
    if (!summary?.tree) {
      return "";
    }

    return convertToMarkdown(summary.tree);
  }, [summary]);

  async function handleSelectFolder() {
    const selected = await selectFolder();

    if (!selected) {
      return;
    }

    setSourceDir(selected);
    setSummary(null);
    setTreeData([]);
  }

  async function handleRun() {
    if (!sourceDir) {
      message.warning("请先选择文件夹");
      return;
    }

    try {
      setLoading(true);
      setSummary(null);
      setTreeData([]);

      const result = await runTool<FolderTreeInput, FolderTreeData>({
        pluginId: "folder-tree",
        input: {
          sourceDir,
          maxDepth,
          includeFiles,
        },
      });

      if (!result.success || !result.data) {
        message.error(result.message);
        return;
      }

      setSummary(result.data);

      if (result.data.tree) {
        setTreeData([convertToTreeData(result.data.tree)]);
      }

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
      title="目录结构查看"
      description="选择一个本地文件夹，获取其目录结构。目录较大时建议使用 Markdown 视图，性能更好，也方便复制。"
      warning={{
        message: "该功能只读取目录结构，不会修改文件",
        description:
          "如果文件数量很多，Tree 视图可能会卡顿。建议适当降低最大深度，或使用 Markdown 视图。",
      }}
      result={
        summary ? (
          <FolderTreeResult
            summary={summary}
            viewMode={viewMode}
            markdownText={markdownText}
            treeData={treeData}
          />
        ) : null
      }
    >
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <ToolPathPicker
          label="目标文件夹"
          value={sourceDir}
          placeholder="请选择需要查看目录结构的文件夹"
          onSelect={handleSelectFolder}
        />

        <Divider style={{ margin: "12px 0" }} />

        <Space wrap>
          <Text strong>扫描选项</Text>

          <Text>最大深度</Text>
          <InputNumber
            min={1}
            max={20}
            value={maxDepth}
            onChange={(value) => setMaxDepth(value ?? 5)}
          />

          <Text>包含文件</Text>
          <Switch checked={includeFiles} onChange={setIncludeFiles} />

          <Text>展示方式</Text>
          <Radio.Group
            value={viewMode}
            onChange={(event) => setViewMode(event.target.value)}
            optionType="button"
            buttonStyle="solid"
            options={[
              {
                label: "Markdown",
                value: "markdown",
              },
              {
                label: "Tree",
                value: "tree",
              },
            ]}
          />
        </Space>

        <Divider style={{ margin: "12px 0" }} />

        <Button
          type="primary"
          icon={<SearchOutlined />}
          loading={loading}
          disabled={!sourceDir}
          onClick={handleRun}
        >
          获取目录结构
        </Button>
      </Space>
    </ToolPageLayout>
  );
}

interface FolderTreeResultProps {
  summary: FolderTreeData;
  viewMode: ViewMode;
  markdownText: string;
  treeData: DataNode[];
}

function FolderTreeResult(props: FolderTreeResultProps) {
  const { summary, viewMode, markdownText, treeData } = props;

  return (
    <Card title="扫描结果">
      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <Space wrap>
          <Text type="secondary">文件夹：{summary.folderCount} 个</Text>
          <Text type="secondary">文件：{summary.fileCount} 个</Text>
          <Text type="secondary">最大深度：{summary.maxDepth}</Text>
          <Text type="secondary">
            包含文件：{summary.includeFiles ? "是" : "否"}
          </Text>
        </Space>

        {viewMode === "markdown" ? (
          <TextArea
            value={markdownText}
            autoSize={{ minRows: 16, maxRows: 32 }}
            readOnly
          />
        ) : null}

        {viewMode === "tree" ? (
          <Tree showLine defaultExpandAll={false} treeData={treeData} />
        ) : null}
      </Space>
    </Card>
  );
}
