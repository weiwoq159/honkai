from auth import login, check_token
from storage import SessionStorage
from nonce import create_nonce
from client import PicaClient
from downloader import download_images


def run_crawl_comic(config: dict) -> dict:
    username = config.get("username")
    password = config.get("password")
    comic_url = config.get("comicUrl")
    storage_dir = config.get("storageDir")

    if not username:
        raise ValueError("缺少 username")

    if not password:
        raise ValueError("缺少 password")

    if not comic_url:
        raise ValueError("缺少 comicUrl")

    logs = []

    logs.append("开始执行哔咔漫画爬虫")
    logs.append(f"漫画地址：{comic_url}")

    storage = SessionStorage(storage_dir=storage_dir)

    account_session = storage.get_account(username)
    token = account_session.get("token") if account_session else None

    if token and check_token(token):
        logs.append("检测到本地 token 可用，跳过登录")
    else:
        logs.append("本地 token 不存在或已失效，开始登录")
        token = login(username=username, password=password)
        logs.append("登录成功，已获取新 token")

    nonce = create_nonce()

    storage.save_account(
        username=username,
        token=token,
        nonce=nonce,
    )

    logs.append("token 和 nonce 已保存")

    client = PicaClient(
        token=token,
        nonce=nonce,
    )

    # TODO:
    # comic_id = client.parse_comic_id(comic_url)
    # comic_detail = client.get_comic_detail(comic_id)
    # chapters = client.get_chapters(comic_id)
    # images = client.get_all_images(comic_id, chapters)
    # download_logs = download_images(images, output_dir)
    # logs.extend(download_logs)

    logs.append("TODO：这里接入漫画详情、章节、图片下载逻辑")
    logs.append("爬取流程执行结束")

    return {
        "action": "crawl_comic",
        "logs": logs,
    }
