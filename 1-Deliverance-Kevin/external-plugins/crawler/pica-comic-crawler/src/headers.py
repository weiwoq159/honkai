from signature import create_signature


def build_headers(
    path: str,
    method: str,
    token: str | None = None,
    nonce: str | None = None,
) -> dict:
    method = method.upper()

    signature = create_signature(
        path=path,
        method=method,
        nonce=nonce,
    )

    headers = {
        "Accept": "application/vnd.picacomic.com.v1+json",
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "okhttp/3.8.1",
        "nonce": nonce or "",
        "signature": signature,
    }

    if token:
        headers["authorization"] = token

    return headers
