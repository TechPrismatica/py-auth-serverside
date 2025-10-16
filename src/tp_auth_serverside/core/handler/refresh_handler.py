import logging

from tp_auth_serverside.db.memorydb.login import get_token, set_token
from tp_auth_serverside.db.memorydb.refresh import is_refresh_restricted, set_restrict_refresh
from tp_auth_serverside.pb import refresh_pb2
from tp_auth_serverside.pb.refresh_pb2_grpc import RefreshServiceServicer
from tp_auth_serverside.utilities.jwt_util import JWTUtil


class RefreshHandler(RefreshServiceServicer):
    async def RefreshToken(self, request, context):
        user_id = request.user_id
        token = request.token
        if await is_refresh_restricted(user_id, token):
            logging.warning(f"Refresh token is restricted for user_id: {user_id}, token: {token}")
            return refresh_pb2.RefreshResponse()
        jwt_token = await get_token(user_id, token)
        if not jwt_token:
            return refresh_pb2.RefreshResponse()
        jwt_util = JWTUtil()
        try:
            logging.info(f"Refreshing token for user_id: {user_id}, token: {token}")
            payload = jwt_util.decode(jwt_token)
            jwt_token = jwt_util.encode(payload=payload)
            await set_token(user_id, jwt_token, short_token=token)
            await set_restrict_refresh(user_id, token)
        except Exception as e:
            logging.error(f"Error refreshing token for user_id: {user_id}, token: {token}, error: {e}")
        return refresh_pb2.RefreshResponse()
