import json
import time
from pathlib import Path
from typing import Any, Dict, Optional
import os

class SessionStorage:
    def __init__(self, storage_dir: str | None = None):
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = (
                Path.home()
                / "AppData"
                / "Roaming"
                / "Honkai"
                / "Gold-Eden"
            )

        self.storage_file = self.storage_dir / "bika-session.json"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> Dict[str, Any]:
        if not self.storage_file.exists():
            return {
                "version": 1,
                "accounts": {},
            }

        try:
            with self.storage_file.open("r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return {
                "version": 1,
                "accounts": {},
            }

    def save_all(self, data: Dict[str, Any]) -> None:
        with self.storage_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def get_account(self, username: str) -> Optional[Dict[str, Any]]:
        data = self.load_all()
        accounts = data.get("accounts") or {}
        return accounts.get(username)

    def save_account(
        self,
        email: str,
        token: str,
        nonce: str | None = None,
    ) -> None:
        data = self.load_all()

        if "accounts" not in data:
            data["accounts"] = {}

        now = int(time.time())
        old_account = data["accounts"].get(email) or {}

        account = {
            **old_account,
            "token": token,
            "tokenUpdatedAt": now,
        }

        if nonce is not None:
            account["nonce"] = nonce
            account["nonceUpdatedAt"] = now

        data["accounts"][email] = account

        self.save_all(data)

    def clear_account(self, username: str) -> None:
        data = self.load_all()
        accounts = data.get("accounts") or {}

        if username in accounts:
            del accounts[username]

        data["accounts"] = accounts
        self.save_all(data)

    def open_storage_dir(self) -> None:
        """
        打开 session 存储目录。
        仅用于调试或工具入口调用。
        """
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        os.startfile(self.storage_dir)


if __name__ == "__main__":
    print("开始调试 SessionStorage")

    storage = SessionStorage()

    print("存储目录：", storage.storage_dir)
    print("存储文件：", storage.storage_file)

    username = "weiwoq158"
    token = "test_token_123"
    nonce = "test_nonce_456"

    print("\n1. 当前全部数据：")
    print(storage.load_all())

    print("\n2. 保存账号 session")
    storage.save_account(
        username=username,
        token=token,
        nonce=nonce,
    )

    print("\n3. 读取全部数据：")
    all_data = storage.load_all()
    print(json.dumps(all_data, ensure_ascii=False, indent=2))

    print("\n4. 读取指定账号：")
    account = storage.get_account(username)
    print(json.dumps(account, ensure_ascii=False, indent=2))

    print("\n5. 清理指定账号")
    storage.clear_account(username)

    print("\n6. 清理后全部数据：")
    print(json.dumps(storage.load_all(), ensure_ascii=False, indent=2))
    storage.open_storage_dir()
    print("\n调试完成")