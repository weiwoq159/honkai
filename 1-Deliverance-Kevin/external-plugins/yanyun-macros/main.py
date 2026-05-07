import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional


PLUGIN_DIR = Path(__file__).resolve().parent

if str(PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(PLUGIN_DIR))


MOCK_PAYLOAD: Dict[str, Any] = {
    "action": "run_lock_farm",
    "config": {
        "loopCount": 2,
        "intervalMs": 2000,
        "dryRun": False,
        "activateWindowBeforeRun": True,
    },
}


USE_MOCK = False


def success(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    成功返回对象。
    注意：这里只返回 dict，不 print。
    """
    return {
        "success": True,
        "message": message,
        "data": data or {},
    }


def fail(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    失败返回对象。
    注意：这里只返回 dict，不 print。
    """
    return {
        "success": False,
        "message": message,
        "data": data or {},
    }


def get_input() -> Dict[str, Any]:
    """
    获取插件入参。

    入参优先级：
    1. USE_MOCK=True 时，直接使用 MOCK_PAYLOAD
    2. 命令行第一个参数
    3. stdin
    4. 没有输入时回退到 MOCK_PAYLOAD
    """
    if USE_MOCK:
        return MOCK_PAYLOAD

    if len(sys.argv) > 1:
        return json.loads(sys.argv[1])

    raw = sys.stdin.read()

    if not raw.strip():
        return MOCK_PAYLOAD

    return json.loads(raw)


def run_app() -> Dict[str, Any]:
    """
    插件主执行入口。

    不要在文件顶部 import MacroContext / MacroRegistry。
    这样即使依赖缺失，也能返回标准 JSON 给前端。
    """
    context = None

    try:
        payload = get_input()

        action = payload.get("action")
        config = payload.get("config") or {}

        if not action:
            return fail(
                "缺少 action",
                {
                    "python": sys.executable,
                    "pluginDir": str(PLUGIN_DIR),
                },
            )

        # 放到这里 import，方便捕获依赖缺失错误
        from core.context import MacroContext
        from macros.registry import MacroRegistry

        context = MacroContext(config)

        registry = MacroRegistry()
        macro_class = registry.get_macro_class(action)

        if macro_class is None:
            return fail(
                f"未知 action: {action}",
                {
                    "action": action,
                    "python": sys.executable,
                    "pluginDir": str(PLUGIN_DIR),
                    "logs": context.logger.get_logs(),
                },
            )

        macro = macro_class(context)

        # execute 会自动执行 before_run / run / after_run
        macro.execute()

        return success(
            f"{macro.name} 执行完成",
            {
                "action": action,
                "python": sys.executable,
                "pluginDir": str(PLUGIN_DIR),
                "logs": context.logger.get_logs(),
            },
        )

    except Exception as error:
        logs = []

        if context is not None:
            try:
                logs = context.logger.get_logs()
            except Exception:
                logs = []

        return fail(
            str(error),
            {
                "python": sys.executable,
                "pluginDir": str(PLUGIN_DIR),
                "logs": logs,
            },
        )


def main() -> None:
    result = run_app()

    # 关键点：
    # stdout 只能输出这一行 JSON。
    # 不要 indent=2，不要在其他地方 print 普通文本。
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()