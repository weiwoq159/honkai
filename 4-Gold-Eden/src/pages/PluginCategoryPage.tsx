import { Card, Col, Empty, Row, Typography } from "antd";
import { useNavigate, useParams } from "react-router-dom";
import { getPluginsByCategory } from "../plugins/registry";
import type { PluginCategory } from "../plugins/types";

const { Paragraph, Text } = Typography;

export function PluginCategoryPage() {
  const navigate = useNavigate();
  const { category } = useParams();

  const pluginCategory = category as PluginCategory;
  const plugins = getPluginsByCategory(pluginCategory);

  return (
    <div
      style={{
        background: "#fff",
        borderRadius: 8,
        padding: 16,
        minHeight: "100%",
      }}
    >
      {plugins.length === 0 ? (
        <Empty description="当前分类下暂无工具" />
      ) : (
        <Row gutter={[16, 16]}>
          {plugins.map((plugin) => (
            <Col xs={24} sm={12} md={8} lg={6} key={plugin.id}>
              <Card
                hoverable
                title={plugin.name}
                onClick={() => navigate(plugin.path)}
                style={{
                  height: "100%",
                  background: "#F3F7FB",
                  border: "1px solid #e5e7eb",
                }}
                styles={{
                  header: {
                    background: "transparent",
                    borderBottom: "1px solid #e5e7eb",
                  },
                  body: {
                    minHeight: 112,
                  },
                }}
              >
                <Paragraph type="secondary" style={{ minHeight: 44 }}>
                  {plugin.description || "暂无描述"}
                </Paragraph>

                <Text type="secondary">点击进入工具页面</Text>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
}
