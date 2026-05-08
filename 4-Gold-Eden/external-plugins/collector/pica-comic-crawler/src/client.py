# src/client.py

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlencode

import requests


# =========================
# 兼容直接运行当前文件
# =========================

CURRENT_DIR = Path(__file__).resolve().parent
PLUGIN_DIR = CURRENT_DIR.parent
PROJECT_DIR = PLUGIN_DIR.parents[2]
SDK_DIR = PROJECT_DIR / "py-runtime" / "sdk"

for item in [CURRENT_DIR, PLUGIN_DIR, SDK_DIR]:
    item_str = str(item)
    if item_str not in sys.path:
        sys.path.insert(0, item_str)


from gold_eden_plugin.logger import get_logger


try:
    from .config import GLOBAL_URL, LOGIN_URL
    from .headers import build_headers
    from .storage import SessionStorage
    from .nonce import generate_nonce
except ImportError:
    from config import GLOBAL_URL, LOGIN_URL
    from headers import build_headers
    from storage import SessionStorage
    from nonce import generate_nonce


PLUGIN_ID = "pica-comic-crawler"

logger = get_logger(PLUGIN_ID)


class PicaClient:
    def __init__(
        self,
        email: str = "",
        password: str = "",
        *,
        storage: Optional[SessionStorage] = None,
        timeout: int = 30,
        max_retries: int = 20,
    ):
        self.email = email.strip().lower()
        self.password = password.strip()
        self.timeout = timeout
        self.max_retries = max_retries

        self.storage = storage or SessionStorage()
        self.session = requests.Session()

        self.token: Optional[str] = None
        self.nonce: Optional[str] = None

        logger.info("初始化 PicaClient")

        self._load_session()

    # =========================
    # Session / Login
    # =========================

    def _load_session(self) -> None:
        """
        从本地缓存中加载 token / nonce。
        """

        if not self.email:
            logger.debug("未传入 email，跳过本地 session 加载")
            return

        account = self.storage.get_account(self.email)

        if not account:
            logger.info(f"未找到本地 session：{self.email}")
            return

        token = account.get("token")
        nonce = account.get("nonce")

        if token:
            self.token = str(token)
            logger.info(f"已加载本地 token：{self.email}")

        if nonce:
            self.nonce = str(nonce)
            logger.debug(f"已加载本地 nonce：{self.email}")

    def ensure_login(self) -> str:
        """
        确保当前 client 有 token。

        有 token：
            直接返回 token

        没 token：
            使用 email/password 登录
        """

        if self.token:
            logger.debug("当前已有 token，跳过登录")
            return self.token

        if not self.email or not self.password:
            raise RuntimeError("当前未登录，请先输入邮箱和密码")

        logger.info("当前无 token，准备登录")

        return self.login()

    def login(self) -> str:
        """
        登录并保存 token。
        """

        if not self.email or not self.password:
            raise RuntimeError("登录失败：email/password 不能为空")

        logger.info(f"开始登录：{self.email}")

        data = self.request(
            "POST",
            LOGIN_URL,
            json_data={
                "email": self.email,
                "password": self.password,
            },
            auth_required=False,
        )

        token = self._extract_token(data)

        if not token:
            raise RuntimeError(f"登录失败：响应中没有 token，response={data}")

        self.token = token

        if not self.nonce:
            self.nonce = generate_nonce()

        self.storage.save_account(
            email=self.email,
            token=self.token,
            nonce=self.nonce,
        )

        logger.info(f"登录成功，session 已保存：{self.email}")

        return self.token

    def reset_login(self) -> str:
        """
        强制重新登录。

        用于：
        - token 失效
        - 用户主动重新登录
        - 401 / 403 后重试
        """

        logger.warning("准备重置登录状态")

        if self.email:
            self.storage.clear_account(self.email)
            logger.info(f"已清理本地 session：{self.email}")

        self.token = None
        self.nonce = generate_nonce()

        return self.login()

    # =========================
    # Request
    # =========================

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        auth_required: bool = True,
        retry_on_auth_failed: bool = True,
    ) -> dict[str, Any]:
        """
        统一请求入口。

        能力：
        - auth_required=True 时，请求前确保有 token
        - 401 / 403 时，重新登录后重试一次
        - 502 / 503 / 504 时，自动重试
        """

        method = method.upper()

        if auth_required:
            self.ensure_login()

        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                logger.info(
                    f"请求接口：{method} {path} "
                    f"attempt={attempt + 1}/{self.max_retries + 1}"
                )

                response = self._send_request(
                    method=method,
                    path=path,
                    params=params,
                    json_data=json_data,
                    auth_required=auth_required,
                )

                logger.debug(
                    f"接口响应：{method} {path} "
                    f"status={response.status_code}"
                )

                if response.status_code in (401, 403):
                    if auth_required and retry_on_auth_failed:
                        logger.warning(
                            f"认证失败，准备重新登录后重试：HTTP {response.status_code}"
                        )

                        self.reset_login()

                        return self.request(
                            method=method,
                            path=path,
                            params=params,
                            json_data=json_data,
                            auth_required=auth_required,
                            retry_on_auth_failed=False,
                        )

                    raise RuntimeError(
                        f"认证失败：HTTP {response.status_code}，{response.text}"
                    )

                if response.status_code in (502, 503, 504):
                    if attempt < self.max_retries:
                        # wait_seconds = 1 + attempt
                        wait_seconds = 1
                        logger.warning(
                            f"接口暂时不可用，准备重试：HTTP {response.status_code}，"
                            f"等待 {wait_seconds}s"
                        )

                        time.sleep(wait_seconds)
                        continue

                    raise RuntimeError(
                        f"服务暂时不可用：HTTP {response.status_code}，{response.text}"
                    )

                response.raise_for_status()

                data = self._parse_json_response(response)

                logger.info(f"请求成功：{method} {path}")

                return data

            except Exception as error:
                last_error = error

                if attempt < self.max_retries:
                    wait_seconds = 1

                    logger.warning(
                        f"请求异常，准备重试：{method} {path}，"
                        f"error={error}，等待 {wait_seconds}s"
                    )

                    time.sleep(wait_seconds)
                    continue

                logger.error(f"请求失败：{method} {path}，error={error}")
                raise

        raise RuntimeError(f"请求失败：{last_error}")

    def get(
        self,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        auth_required: bool = True,
    ) -> dict[str, Any]:
        return self.request(
            "GET",
            path,
            params=params,
            auth_required=auth_required,
        )

    def post(
        self,
        path: str,
        *,
        json_data: Optional[dict[str, Any]] = None,
        auth_required: bool = True,
    ) -> dict[str, Any]:
        return self.request(
            "POST",
            path,
            json_data=json_data,
            auth_required=auth_required,
        )

    def _send_request(
        self,
        *,
        method: str,
        path: str,
        params: Optional[dict[str, Any]],
        json_data: Optional[dict[str, Any]],
        auth_required: bool,
    ) -> requests.Response:
        time_value = self._current_time()
        nonce = self._get_or_create_nonce()

        signature_path = self._build_signature_path(path, params)
        url = self._build_url(path)

        headers = build_headers(
            time_value=time_value,
            nonce=nonce,
            path=signature_path,
            method=method,
            token=self.token if auth_required else None,
        )

        logger.debug(f"请求 URL：{url}")
        logger.debug(f"签名 path：{signature_path}")

        return self.session.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            headers=headers,
            timeout=self.timeout,
        )

    # =========================
    # API Methods
    # =========================

    def get_comic_detail(self, comic_id: str) -> dict[str, Any]:
        return self.get(f"comics/{comic_id}")

    def get_chapters(
        self,
        comic_id: str,
        *,
        page: int = 1,
    ) -> dict[str, Any]:
        return self.get(
            f"comics/{comic_id}/eps",
            params={
                "page": page,
            },
        )

    def get_chapter_pages(
        self,
        comic_id: str,
        chapter_order: int,
        *,
        page: int = 1,
    ) -> dict[str, Any]:
        return self.get(
            f"comics/{comic_id}/order/{chapter_order}/pages",
            params={
                "page": page,
            },
        )

    # =========================
    # Helpers
    # =========================

    def _build_url(self, path: str) -> str:
        base_url = GLOBAL_URL.rstrip("/")
        clean_path = path.lstrip("/")
        return f"{base_url}/{clean_path}"

    def _build_signature_path(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> str:
        clean_path = path.lstrip("/")

        if not params:
            return clean_path

        query = urlencode(params)

        if "?" in clean_path:
            return f"{clean_path}&{query}"

        return f"{clean_path}?{query}"

    def _get_or_create_nonce(self) -> str:
        if self.nonce:
            return self.nonce

        if self.email:
            account = self.storage.get_account(self.email)

            if account and account.get("nonce"):
                self.nonce = str(account["nonce"])
                return self.nonce

        self.nonce = generate_nonce()
        logger.debug("已生成新的 nonce")

        return self.nonce

    def _current_time(self) -> str:
        return str(int(time.time()))

    def _parse_json_response(self, response: requests.Response) -> dict[str, Any]:
        try:
            data = response.json()
        except Exception as error:
            raise RuntimeError(f"响应不是合法 JSON：{response.text}") from error

        if not isinstance(data, dict):
            raise RuntimeError(f"响应 JSON 不是对象：{data}")

        return data

    def _extract_token(self, data: dict[str, Any]) -> Optional[str]:
        """
        兼容几种常见 token 返回结构。
        """

        candidates = [
            data.get("token"),
            data.get("data", {}).get("token")
            if isinstance(data.get("data"), dict)
            else None,
            data.get("data", {}).get("authToken")
            if isinstance(data.get("data"), dict)
            else None,
            data.get("data", {}).get("jwt")
            if isinstance(data.get("data"), dict)
            else None,
        ]

        for item in candidates:
            if item:
                return str(item)

        return None


if __name__ == "__main__":
    client = PicaClient(
        email="weiwoq158",
        password="Cq0932313123!",
    )

    logger.info("开始调试 PicaClient")
    logger.info(f"当前 token：{client.token}")

    try:
        token = client.ensure_login()
        logger.info(f"登录 token：{token}")

        # 测试详情接口
        # result = client.get_comic_detail("69f4eb4f96a7f803b14d4dd0")
        # logger.info(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as error:
        logger.exception(f"PicaClient 调试失败：{error}")