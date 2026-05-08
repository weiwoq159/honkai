def login(username: str, password: str) -> str:
    """
    登录并返回 token。

    TODO:
    替换成你的真实登录接口。
    """
    raise NotImplementedError("请先实现 auth.login")


def check_token(token: str) -> bool:
    """
    校验 token 是否可用。

    TODO:
    建议调用一个轻量接口验证 token。
    """
    if not token:
        return False

    return False
