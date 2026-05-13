import { Card, Typography } from "antd";

const { Title, Paragraph } = Typography;

export function FolderFlattenerPage() {
  return (
    <Card>
      <Title level={3}>拉平文件夹</Title>
      <Paragraph>
        将多层文件夹中的文件提取到目标目录，支持重名处理
      </Paragraph>
    </Card>
  );
}
