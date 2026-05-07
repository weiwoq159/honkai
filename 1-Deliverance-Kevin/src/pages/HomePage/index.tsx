import { Card, Col, Row, Typography } from "antd";
import { useNavigate } from "react-router-dom";
import { plugins } from "../../plugins/registry";

const { Title, Paragraph, Text } = Typography;

export function HomePage() {
  const navigate = useNavigate();

  return (
    <div>
      <section style={{ marginBottom: 24 }}>
        <Title level={2} style={{ marginBottom: 8 }}>
          工具箱
        </Title>

        <Paragraph style={{ marginBottom: 0, color: "#6b7280" }}>
          集中管理本地常用工具，例如文件处理、图片去重、图片下载、视频处理等。
        </Paragraph>
      </section>

      <Row gutter={[16, 16]}>
        {plugins.map((plugin) => (
          <Col key={plugin.id} xs={24} sm={12} lg={8} xl={6}>
            <Card
              hoverable
              onClick={() => navigate(plugin.path)}
              style={{ height: "100%" }}
            >
              <Title level={4} style={{ marginTop: 0 }}>
                {plugin.name}
              </Title>

              <Paragraph style={{ color: "#6b7280", minHeight: 44 }}>
                {plugin.description}
              </Paragraph>

              <Text type="secondary">{plugin.category}</Text>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}
