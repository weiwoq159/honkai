# pica-comic-crawler

哔咔漫画爬虫插件。

## 功能

- 接收前端传入的用户名、密码、漫画地址
- 检查本地 token 是否可用
- token 不可用时执行登录
- 生成 nonce / signature
- 获取漫画章节和图片
- 下载图片
- 返回执行日志

## 入参示例

{
  "action": "crawl_comic",
  "config": {
    "username": "your_username",
    "password": "your_password",
    "comicUrl": "https://xxx/xxx"
  }
}
