import { open } from "@tauri-apps/plugin-dialog";
import { message } from "antd";

export const selectFolder = async (): Promise<string | null> => {
  const selected = await open({
    multiple: false,
    directory: true,
    title: "选择文件夹",
  });

  if (typeof selected !== "string") {
    return null;
  }

  return selected;
};

export const showMessage = (messageStr: string) => {
  message.success({
    content: messageStr,
  });
};
