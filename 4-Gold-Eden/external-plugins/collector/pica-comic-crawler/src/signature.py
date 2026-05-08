# signature_generator.py

import base64
import hashlib
import hmac


SECRET_1_ENC = "b397e2wXZHtgb2RvUBh7bnB+bnt8bEEfZ2xSQUFtY0F4G3h4bWhzeA=="
SECRET_2_ENC = "aGh+G0dwfHpGUGRmYGxrGUFsZmRyGUMZa19kfUxfRxMfXGAaGxNBbmBhZRpMQUFma20Bbn58YElIYGQTbGdsQkxrfEd8X3xueBocH1JQf2RpSG9B"


def shuffle_decode(text: str, seed_text: str) -> str:
    """
    对应 JS 里的 ge(e, t)
    """
    index_list = list(range(len(text)))

    seed = 0
    for ch in seed_text:
        seed += ord(ch)

    for i in range(len(index_list) - 1, 0, -1):
        seed = (9301 * seed + 49297) % 233280
        j = seed % (i + 1)
        index_list[i], index_list[j] = index_list[j], index_list[i]

    chars = list(text)
    result = [""] * len(text)

    for i in range(len(chars)):
        result[i] = chars[index_list[i]]

    return "".join(result)


def decode_secret(encoded: str) -> str:
    """
    对应 JS 里的 pe(e)

    JS 逻辑：
    1. atob(e)
    2. ge(..., "PicaWeb2025")
    3. 每个字符 xor 42
    4. 再 atob(...)
    """
    first = base64.b64decode(encoded).decode("latin1")

    shuffled = shuffle_decode(first, "PicaWeb2025")

    xored = "".join(
        chr(ord(ch) ^ 42)
        for ch in shuffled
    )

    return base64.b64decode(xored).decode("latin1")


def generate_signature(
    time_value: str,
    nonce: str,
    path: str,
    method: str = "GET",
) -> str:
    """
    对应 JS 里的 Ce(e, t, o)

    JS 原始逻辑：
    let i = e.replace(r, "") + t + Se() + o + n;
    i = i.toLowerCase();

    这里已经把 e.replace(r, "") 简化成 path。
    所以 raw = path + time + nonce + method + secret_1
    """

    secret_1 = decode_secret(SECRET_1_ENC)
    secret_2 = decode_secret(SECRET_2_ENC)

    raw = f"{path}{time_value}{nonce}{method}{secret_1}".lower()

    return hmac.new(
        secret_2.encode("utf-8"),
        raw.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()




