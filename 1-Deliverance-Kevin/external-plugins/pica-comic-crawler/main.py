import json
import sys


def run(input_data: dict) -> dict:
    return {
        "success": True,
        "message": "插件执行成功",
        "data": input_data
    }


if __name__ == "__main__":
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input) if raw_input else {}

        result = run(input_data)

        print(json.dumps(result, ensure_ascii=True))

    except Exception as error:
        result = {
            "success": False,
            "message": str(error),
            "data": None
        }

        print(json.dumps(result, ensure_ascii=True))
        sys.exit(1)
