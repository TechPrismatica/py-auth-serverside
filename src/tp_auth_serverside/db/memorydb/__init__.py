import asyncio

from mem_db_utils.asyncio import MemDBConnector
from redis import Redis

from tp_auth_serverside.config import Database

mem_connector = MemDBConnector()

login_db: Redis = asyncio.run(mem_connector.connect(db=Database.login_redis_db, decode_response=True))
refresh_restrict_db: Redis = asyncio.run(mem_connector.connect(db=Database.refresh_restrict_db, decode_response=True))
