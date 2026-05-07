export interface FolderTreeInput {
  sourceDir: string;
  maxDepth?: number;
  includeFiles?: boolean;
}

export interface FolderTreeNode {
  name: string;
  path: string;
  relativePath: string;
  type: "directory" | "file";
  size?: number;
  truncated?: boolean;
  error?: string;
  children?: FolderTreeNode[];
}

export interface FolderTreeData {
  sourceDir: string;
  maxDepth: number;
  includeFiles: boolean;
  folderCount: number;
  fileCount: number;
  tree: FolderTreeNode;
}
