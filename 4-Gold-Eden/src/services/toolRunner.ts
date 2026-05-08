import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";

export interface RunToolInput<TConfig = Record<string, unknown>> {
  action: string;
  config: TConfig;
}

export interface RunToolPayload<TConfig = Record<string, unknown>> {
  pluginId: string;
  input: RunToolInput<TConfig>;
}

export interface RunToolResult<TData = unknown> {
  success: boolean;
  message: string;
  data?: TData | null;
  logs?: string[];
}

export interface ToolEventPayload<TData = unknown> {
  pluginId: string;
  data: TData;
}

export function runTool<TData = unknown, TConfig = Record<string, unknown>>(
  payload: RunToolPayload<TConfig>,
): Promise<RunToolResult<TData>> {
  return invoke<RunToolResult<TData>>("run_tool", {
    payload,
  });
}

export function listenToolProgress<TData = unknown>(
  callback: (payload: ToolEventPayload<TData>) => void,
) {
  return listen<ToolEventPayload<TData>>("tool-progress", (event) => {
    callback(event.payload);
  });
}

export function listenToolLog<TData = unknown>(
  callback: (payload: ToolEventPayload<TData>) => void,
) {
  return listen<ToolEventPayload<TData>>("tool-log", (event) => {
    callback(event.payload);
  });
}
