# scripts/nonce/nonce_generator.py

import random
from pathlib import Path


NONCE_CHARS = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"

NONCE_FILE = Path(__file__).resolve().parent / "nonce.txt"


def generate_nonce(length: int = 32) -> str:
    return "".join(
        random.choice(NONCE_CHARS)
        for _ in range(length)
    ).lower()


def get_or_create_nonce() -> str:
    if NONCE_FILE.exists():
        nonce = NONCE_FILE.read_text(encoding="utf-8").strip()
        if nonce:
            return nonce

    nonce = generate_nonce()
    NONCE_FILE.write_text(nonce, encoding="utf-8")
    return nonce


def set_nonce(nonce: str) -> None:
    nonce = nonce.strip()

    if not nonce:
        raise ValueError("nonce 不能为空")

    NONCE_FILE.write_text(nonce, encoding="utf-8")