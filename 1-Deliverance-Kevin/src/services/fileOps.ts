import { invoke } from "@tauri-apps/api/core";

export interface DeleteFilesPayload {
  filePaths: string[];
}

export interface DeleteFileItemResult {
  path: string;
  success: boolean;
  message: string;
}

export interface DeleteFilesResult {
  success: boolean;
  message: string;
  deletedCount: number;
  failedCount: number;
  items: DeleteFileItemResult[];
}

export function moveFilesToTrash(
  payload: DeleteFilesPayload,
): Promise<DeleteFilesResult> {
  return invoke<DeleteFilesResult>("move_files_to_trash", {
    payload,
  });
}
