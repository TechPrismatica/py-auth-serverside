from tp_auth_serverside.config import Secrets
from tp_auth_serverside.db.memorydb import refresh_restrict_db


async def set_restrict_refresh(user_id: str, token: str) -> None:
    await refresh_restrict_db.set(f"{user_id}__{token}", "restricted", ex=Secrets.refresh_restrict_minutes * 60)


async def is_refresh_restricted(user_id: str, token: str) -> bool:
    return await refresh_restrict_db.exists(f"{user_id}__{token}") == 1
