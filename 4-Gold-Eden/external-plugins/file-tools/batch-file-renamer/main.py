import json
import sys


def main():
    result = {
        "success": True,
        "message": "批量重命名 执行完成",
        "data": {
            "pluginId": "batch-file-renamer",
            "name": "批量重命名"
        },
        "logs": [
            "[INFO] 批量重命名 开始执行",
            "[SUCCESS] 批量重命名 执行完成"
        ]
    }

    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
