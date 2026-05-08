from __future__ import annotations

try:
    from .signature import generate_signature
except ImportError:
    from signature import generate_signature

def build_headers(
    time_value: str,
    nonce: str,
    path: str,
    method: str = "GET",
    token: str | None = None,
) -> dict:
    signature = generate_signature(
        time_value=time_value,
        nonce=nonce,
        path=path,
        method=method,
    )

    headers = {
        "app-channel": "1",
        "app-uuid": "webUUIDv2",
        "app-version": "20251017",
        "accept": "application/vnd.picacomic.com.v1+json",
        "app-platform": "android",
        "Content-Type": "application/json; charset=UTF-8",
        "time": time_value,
        "nonce": nonce,
        "image-quality": "medium",
        "signature": signature,
        "origin": "https://manhuabika.com",
        "referer": "https://manhuabika.com/",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/147.0.0.0 Safari/537.36"
        ),
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "accept-encoding": "identity",
    }

    if token:
        headers["authorization"] = token

    return headers


if __name__ == "__main__":
    import json

    headers = build_headers(
        time_value="1778172934",
        nonce="test_nonce",
        path="auth/sign-in",
        method="POST",
        token=None,
    )

    print(json.dumps(headers, ensure_ascii=False, indent=2))