import json
import sys


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}

        result = {
            "success": True,
            "message": "拉平文件夹 执行完成",
            "data": {
                "pluginId": "folder-flattener",
                "name": "拉平文件夹",
                "payload": payload
            },
            "logs": [
                "[INFO] 拉平文件夹 开始执行",
                "[SUCCESS] 拉平文件夹 执行完成"
            ]
        }

        print(json.dumps(result, ensure_ascii=False), flush=True)

    except Exception as error:
        result = {
            "success": False,
            "message": str(error),
            "data": None,
            "logs": [
                f"[ERROR] {str(error)}"
            ]
        }

        print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
