import requests

from headers import build_headers


class PicaClient:
    def __init__(self, token: str, nonce: str):
        self.token = token
        self.nonce = nonce
        self.base_url = "https://picaapi.picacomic.com"

    def get(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"

        headers = build_headers(
            path=path,
            method="GET",
            token=self.token,
            nonce=self.nonce,
        )

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

    def post(self, path: str, data: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"

        headers = build_headers(
            path=path,
            method="POST",
            token=self.token,
            nonce=self.nonce,
        )

        response = requests.post(
            url,
            json=data or {},
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

    def parse_comic_id(self, comic_url: str) -> str:
        return comic_url.rstrip("/").split("/")[-1]

    def get_comic_detail(self, comic_id: str) -> dict:
        return self.get(f"/comics/{comic_id}")

    def get_chapters(self, comic_id: str) -> dict:
        return self.get(f"/comics/{comic_id}/eps")

    def get_chapter_pages(
        self,
        comic_id: str,
        chapter_order: int,
        page: int = 1,
    ) -> dict:
        return self.get(
            f"/comics/{comic_id}/order/{chapter_order}/pages",
            params={"page": page},
        )
