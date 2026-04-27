import type { RustCommands } from "../types/RustCommands";
import { invoke } from "@tauri-apps/api/core";

export const invokeRust = async <K extends keyof RustCommands>(
  command: K, // 必须是 RustCommands 中定义过的命令
  args: RustCommands[K]["args"], // 自动获取 args 类型
): Promise<RustCommands[K]["return"]> => {
  // 自动推断返回值类型
  try {
    return await invoke<RustCommands[K]["return"]>(command, args);
  } catch (error) {
    console.error(`调用 ${command} 失败`, error);
    throw error;
  }
};
