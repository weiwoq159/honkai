import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR))

def main():
    result = {
        "success": True,
        "message": "刷锁宏 执行完成",
        "data": {
            "pluginId": "yanyun-lock-macro",
            "name": "刷锁宏"
        },
        "logs": [
            "[INFO] 刷锁宏 开始执行",
            "[SUCCESS] 刷锁宏 执行完成"
        ]
    }

    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
