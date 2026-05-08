import sys
import json
import traceback
from pathlib import Path

from crawler import run_crawl_comic
from result import success_result, error_result


def read_payload() -> dict:
    raw = ""
    print("cwd =", Path.cwd(), flush=True)
    print("argv =", sys.argv, flush=True)
    if not sys.stdin.isatty():
        raw = sys.stdin.read()

    if raw.strip():
        return json.loads(raw)

    if len(sys.argv) >= 3 and sys.argv[1] == "--input":
        input_file = Path(sys.argv[2])
        return json.loads(input_file.read_text(encoding="utf-8"))

    debug_file = Path(__file__).resolve().parents[1] / "fixtures" / "debug_input.json"

    if debug_file.exists():
        return json.loads(debug_file.read_text(encoding="utf-8"))

    raise ValueError("未收到 stdin 输入，也没有找到 debug_input.json")


def main():
    try:
        payload = read_payload()

        action = payload.get("action")
        config = payload.get("config") or {}

        if action == "crawl_comic":
            data = run_crawl_comic(config)
            result = success_result(
                message="哔咔爬虫执行完成",
                data=data,
            )
        else:
            raise ValueError(f"不支持的 action: {action}")

    except Exception as error:
        result = error_result(
            message=str(error),
            logs=[traceback.format_exc()],
        )

    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()