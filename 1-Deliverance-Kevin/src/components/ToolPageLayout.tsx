import type { ReactNode } from "react";
import { Alert, Card, Space, Typography } from "antd";

const { Title, Paragraph } = Typography;

interface ToolPageLayoutProps {
  title: string;
  description?: ReactNode;
  warning?: {
    message: string;
    description?: string;
  };
  children: ReactNode;
  result?: ReactNode;
}

export function ToolPageLayout(props: ToolPageLayoutProps) {
  const { title, description, warning, children, result } = props;

  return (
    <Space direction="vertical" size={16} style={{ width: "100%" }}>
      <Card>
        <Title level={3} style={{ marginTop: 0 }}>
          {title}
        </Title>

        {description ? (
          <Paragraph type="secondary">{description}</Paragraph>
        ) : null}

        {warning ? (
          <Alert
            type="warning"
            showIcon
            message={warning.message}
            description={warning.description}
            style={{ marginBottom: 16 }}
          />
        ) : null}

        {children}
      </Card>

      {result}
    </Space>
  );
}
