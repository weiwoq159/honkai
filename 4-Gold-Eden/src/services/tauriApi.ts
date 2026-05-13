import { invoke } from "@tauri-apps/api/core";

export type ApiResponse<TData = unknown> = {
  code: number;
  message: string;
  data: TData | null;
};

export type TavernCharacterSummary = {
  id: string;
  name: string;
  avatarPath?: string | null;
  characterPath: string;
  description?: string | null;
  updatedAt?: number | null;
};

async function invokeApi<TData>(
  command: string,
  args?: Record<string, unknown>,
): Promise<TData> {
  const response = await invoke<ApiResponse<TData>>(command, args);

  if (response.code !== 0) {
    throw new Error(response.message || "请求失败");
  }

  if (response.data === null) {
    throw new Error(response.message || "返回数据为空");
  }

  return response.data;
}

export function listTavernCharacters() {
  return invokeApi<TavernCharacterSummary[]>("list_tavern_characters");
}
