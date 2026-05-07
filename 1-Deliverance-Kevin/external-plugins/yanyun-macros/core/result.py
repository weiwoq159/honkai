from typing import Any, Dict, Optional


class PluginResult:
    @staticmethod
    def success(
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "success": True,
            "message": message,
            "data": data or {},
        }

    @staticmethod
    def fail(
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "success": False,
            "message": message,
            "data": data or {},
        }