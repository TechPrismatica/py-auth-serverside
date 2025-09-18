import asyncio

from tp_auth_serverside.db.memorydb.login import get_token, set_token
from tp_auth_serverside.db.memorydb.refresh import is_refresh_restricted, set_restrict_refresh
from tp_auth_serverside.pb.refresh_pb2_grpc import RefreshServiceServicer
from tp_auth_serverside.utilities.jwt_util import JWTUtil


class RefreshHandler(RefreshServiceServicer):
    @staticmethod
    def RefreshToken(request, context):
        user_id = request.user_id
        token = request.token
        if asyncio.run(is_refresh_restricted(user_id, token)):
            return None  # Since the response type is google.protobuf.empty_pb2.Empty
        jwt_token = asyncio.run(get_token(user_id, token))
        if not jwt_token:
            return None  # Since the response type is google.protobuf.empty_pb2.Empty
        jwt_util = JWTUtil()
        try:
            payload = jwt_util.decode(jwt_token)
            jwt_token = jwt_util.encode(payload=payload)
            asyncio.run(set_token(user_id, jwt_token, short_token=token))
            asyncio.run(set_restrict_refresh(user_id, token))
        except Exception:
            pass
        return None  # Since the response type is google.protobuf.empty_pb2.Empty
