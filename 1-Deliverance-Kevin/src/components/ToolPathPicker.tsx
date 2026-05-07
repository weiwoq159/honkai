import { Button, Input, Space, Typography } from "antd";
import { FolderOpenOutlined } from "@ant-design/icons";

const { Text } = Typography;

interface ToolPathPickerProps {
  label: string;
  value: string;
  placeholder?: string;
  onSelect: () => void;
}

export function ToolPathPicker(props: ToolPathPickerProps) {
  const { label, value, placeholder = "请选择文件夹", onSelect } = props;

  return (
    <div>
      <Text strong>{label}</Text>

      <Space.Compact style={{ width: "100%", marginTop: 8 }}>
        <Input value={value} disabled placeholder={placeholder} />

        <Button icon={<FolderOpenOutlined />} onClick={onSelect}>
          选择文件夹
        </Button>
      </Space.Compact>
    </div>
  );
}
