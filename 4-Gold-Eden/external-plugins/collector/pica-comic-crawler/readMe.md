D:\work\mq\Honkai\4-Gold-Eden\
│
├─ py-runtime
│  └─ sdk
│     └─ gold_eden_plugin
│        ├─ __init__.py
│        ├─ logger.py              # 通用日志 + 进度事件
│        ├─ result.py              # success / fail / PluginResult
│        └─ runner.py              # run_plugin / run_with_input
│
└─ external-plugins
   └─ collector
      └─ pica-comic-crawler
         │
         ├─ fixtures
         │  ├─ debug_input.json    # 本地调试入参
         │  ├─ pica_response.json  # 接口响应样例，可选
         │  └─ script.js           # JS 签名参考脚本，可选
         │
         ├─ src
         │  ├─ utils
         │  │  ├─ __init__.py
         │  │  ├─ url_parser.py    # 从 URL 中提取 comic_id
         │  │  ├─ image_url.py     # 拼接图片地址
         │  │  └─ file_utils.py    # 文件名清洗、目录创建
         │  │
         │  ├─ __init__.py
         │  ├─ config.py           # 固定配置：接口域名、路径、timeout
         │  ├─ storage.py          # 用户电脑缓存：token / nonce
         │  ├─ nonce.py            # nonce 生成/读取逻辑
         │  ├─ signature.py        # signature 签名生成
         │  ├─ headers.py          # 请求头构建
         │  ├─ auth.py             # 登录 / token 判断
         │  ├─ client.py           # HTTP 请求封装
         │  ├─ crawler.py          # 主采集流程
         │  └─ downloader.py       # 图片下载
         │
         ├─ .gitignore
         ├─ main.py                # 插件入口，只调用 run_plugin
         ├─ plugin.json            # 插件元信息
         ├─ README.md
         └─ requirements.txt