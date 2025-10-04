import logging

from tp_auth_serverside.config import Secrets
from tp_auth_serverside.db.memorydb import refresh_restrict_db


async def set_restrict_refresh(user_id: str, token: str) -> None:
    logging.info(f"Setting refresh restrict for user_id: {user_id}, token: {token}")
    await refresh_restrict_db.set(f"{user_id}__{token}", "restricted", ex=Secrets.refresh_restrict_minutes * 60)


async def is_refresh_restricted(user_id: str, token: str) -> bool:
    result = await refresh_restrict_db.exists(f"{user_id}__{token}")
    logging.info(f"Checking refresh restrict for user_id: {user_id}, token: {token}, exists: {result}")
    return result == 1
