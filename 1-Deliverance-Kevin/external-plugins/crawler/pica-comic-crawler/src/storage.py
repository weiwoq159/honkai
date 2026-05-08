import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


class SessionStorage:
    def __init__(self, storage_dir: str | None = None):
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = (
                Path.home()
                / "AppData"
                / "Roaming"
                / "FurinaTools"
                / "plugins"
                / "pica-comic-crawler"
            )

        self.storage_file = self.storage_dir / "session.json"
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
        username: str,
        token: str,
        nonce: str | None = None,
    ) -> None:
        data = self.load_all()

        if "accounts" not in data:
            data["accounts"] = {}

        now = int(time.time())
        old_account = data["accounts"].get(username) or {}

        account = {
            **old_account,
            "token": token,
            "tokenUpdatedAt": now,
        }

        if nonce is not None:
            account["nonce"] = nonce
            account["nonceUpdatedAt"] = now

        data["accounts"][username] = account

        self.save_all(data)

    def clear_account(self, username: str) -> None:
        data = self.load_all()
        accounts = data.get("accounts") or {}

        if username in accounts:
            del accounts[username]

        data["accounts"] = accounts
        self.save_all(data)
