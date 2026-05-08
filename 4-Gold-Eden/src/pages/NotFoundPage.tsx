import { Button, Result } from "antd";
import { useNavigate } from "react-router-dom";

export function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <Result
      status="404"
      title="页面不存在"
      subTitle="当前页面不存在，或者对应插件页面尚未注册。"
      extra={
        <Button type="primary" onClick={() => navigate("/")}>
          返回 Dashboard
        </Button>
      }
    />
  );
}
