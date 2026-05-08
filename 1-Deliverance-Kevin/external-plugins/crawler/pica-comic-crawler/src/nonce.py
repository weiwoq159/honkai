import uuid


def create_nonce() -> str:
    return str(uuid.uuid4())
