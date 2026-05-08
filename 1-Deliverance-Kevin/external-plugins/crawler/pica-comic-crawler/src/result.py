from typing import Any, Dict, List, Optional


def success_result(
    message: str,
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": data or {},
    }


def error_result(
    message: str,
    logs: Optional[List[str]] = None,
) -> Dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "data": {
            "logs": logs or [],
        },
    }
