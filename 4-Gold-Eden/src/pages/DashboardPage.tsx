import { Card, Col, Row, Space, Statistic, Typography } from "antd";
import { frontendPlugins, pluginCategories } from "../plugins/registry";

const { Title, Paragraph } = Typography;

export function DashboardPage() {
  return (
    <Space direction="vertical" size={16} style={{ width: "100%" }}>
      <div>
        <Title level={3}>Dashboard</Title>
        <Paragraph type="secondary">
          本地采集、自动化和文件处理工具的统一入口。
        </Paragraph>
      </div>

      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic title="插件总数" value={frontendPlugins.length} />
          </Card>
        </Col>

        <Col span={8}>
          <Card>
            <Statistic title="工具分类" value={pluginCategories.length} />
          </Card>
        </Col>

        <Col span={8}>
          <Card>
            <Statistic title="最近执行" value="暂无" />
          </Card>
        </Col>
      </Row>

      <Card title="插件分类">
        <Row gutter={[16, 16]}>
          {pluginCategories.map((category) => {
            const count = frontendPlugins.filter(
              (plugin) => plugin.category === category.key,
            ).length;

            return (
              <Col span={8} key={category.key}>
                <Card size="small">
                  <Statistic title={category.name} value={count} />
                </Card>
              </Col>
            );
          })}
        </Row>
      </Card>

      <Card title="快捷入口">
        <Row gutter={[16, 16]}>
          {frontendPlugins
            .slice()
            .sort((a, b) => a.order - b.order)
            .slice(0, 6)
            .map((plugin) => (
              <Col span={8} key={plugin.id}>
                <Card size="small" title={plugin.name}>
                  <Paragraph type="secondary" style={{ marginBottom: 0 }}>
                    {plugin.description || "暂无描述"}
                  </Paragraph>
                </Card>
              </Col>
            ))}
        </Row>
      </Card>
    </Space>
  );
}
