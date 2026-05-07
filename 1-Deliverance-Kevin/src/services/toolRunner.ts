import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";

export interface RunToolPayload<TInput = Record<string, unknown>> {
  pluginId: string;
  input: TInput;
}

export interface RunToolResult<TData = unknown> {
  success: boolean;
  message: string;
  data?: TData | null;
}

export interface ToolEventPayload<TData = unknown> {
  pluginId: string;
  data: TData;
}

export function runTool<TInput = Record<string, unknown>, TData = unknown>(
  payload: RunToolPayload<TInput>,
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
