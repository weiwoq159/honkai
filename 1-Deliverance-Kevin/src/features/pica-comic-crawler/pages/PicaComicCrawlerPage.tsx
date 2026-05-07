import { Card, Typography } from "antd";

const { Title, Paragraph } = Typography;

export function PicaComicCrawlerPage() {
  return (
    <Card>
      <Title level={3} style={{ marginTop: 0 }}>
        哔咔漫画爬取
      </Title>

      <Paragraph type="secondary">
        根据章节分页接口下载漫画图片
      </Paragraph>
    </Card>
  );
}
