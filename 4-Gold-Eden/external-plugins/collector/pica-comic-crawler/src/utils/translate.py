import requests
TRANSLATE_API_URL = "https://translate.googleapis.com/translate_a/single"
TRANSLATE_TIMEOUT_SECONDS = 15
TRANSLATE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/136.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
}

def contains_cjk(text: str) -> bool:
    for char in text:
        code = ord(char)

        if (
            0x3040 <= code <= 0x30FF
            or 0x3400 <= code <= 0x4DBF
            or 0x4E00 <= code <= 0x9FFF
            or 0xF900 <= code <= 0xFAFF
        ):
            return True

    return False

def translate_to_simplified_chinese(text: str) -> str:
    normalized_text = (text or "").strip()

    if not normalized_text or not contains_cjk(normalized_text):
        return normalized_text

    response = requests.get(
        TRANSLATE_API_URL,
        params={
            "client": "gtx",
            "sl": "auto",
            "tl": "zh-CN",
            "dt": "t",
            "q": normalized_text,
        },
        headers=TRANSLATE_HEADERS,
        timeout=TRANSLATE_TIMEOUT_SECONDS,
    )

    response.raise_for_status()

    payload = response.json()
    segments = payload[0] if isinstance(payload, list) and payload else []

    translated_text = "".join(
        segment[0]
        for segment in segments
        if isinstance(segment, list) and segment and isinstance(segment[0], str)
    ).strip()

    return translated_text or normalized_text