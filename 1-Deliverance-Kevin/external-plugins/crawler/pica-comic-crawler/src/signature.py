import hashlib
import hmac


def create_signature(
    path: str,
    method: str,
    nonce: str | None = None,
) -> str:
    """
    生成 signature。

    TODO:
    替换成你已经逆出来的真实签名逻辑。
    """
    secret = "TODO_SECRET"
    raw = f"{path}{method.lower()}{nonce or ''}"

    return hmac.new(
        secret.encode("utf-8"),
        raw.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
