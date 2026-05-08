import { Card, Form, Input, Space, Switch, Typography } from "antd";

const { Title, Paragraph, Text } = Typography;

export function SettingsPage() {
  return (
    <Space direction="vertical" size={16} style={{ width: "100%" }}>
      <div>
        <Title level={3}>设置</Title>
        <Paragraph type="secondary">
          配置本地运行环境、插件目录和执行偏好。
        </Paragraph>
      </div>

      <Card title="基础设置">
        <Form layout="vertical">
          <Form.Item label="插件目录">
            <Input
              disabled
              value="external-plugins"
              placeholder="插件目录暂未开放修改"
            />
          </Form.Item>

          <Form.Item label="Python 命令">
            <Input
              disabled
              value="python"
              placeholder="后续可支持自定义 Python 路径"
            />
          </Form.Item>

          <Form.Item label="默认下载目录">
            <Input disabled placeholder="后续可支持自定义下载目录" />
          </Form.Item>
        </Form>
      </Card>

      <Card title="执行设置">
        <Space direction="vertical" size={12}>
          <Space>
            <Switch checked disabled />
            <Text>执行失败时保留错误日志</Text>
          </Space>

          <Space>
            <Switch checked disabled />
            <Text>插件 stdout 仅允许输出最终 JSON</Text>
          </Space>

          <Space>
            <Switch disabled />
            <Text>启用实时进度事件推送</Text>
          </Space>
        </Space>
      </Card>

      <Card title="说明">
        <Paragraph type="secondary" style={{ marginBottom: 0 }}>
          当前设置页先作为占位页面。后续可以在这里配置 Python
          路径、插件下载目录、默认输出目录、日志保存策略和插件运行环境。
        </Paragraph>
      </Card>
    </Space>
  );
}
