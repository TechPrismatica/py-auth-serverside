import shortuuid

from tp_auth_serverside.config import Secrets
from tp_auth_serverside.db.memorydb import login_db


async def set_token(user_id: str, token: str, expire_minutes: int = Secrets.expiry, short_token: str = None) -> str:
    short_token = short_token or shortuuid.uuid(name=user_id)
    await login_db.hset(user_id, short_token, {"token": token, "expire": expire_minutes})
    await login_db.hexpire(user_id, expire_minutes * 60, fields=[short_token])
    return short_token


async def get_token(user_id: str, short_token: str) -> str | None:
    token_data = await login_db.hget(user_id, short_token)
    if token_data:
        return token_data.get("token")
    return None
