from fastapi import Response

from tp_auth_serverside.auth.user_specs import UserInfoSchema
from tp_auth_serverside.db.memorydb.login import revoke_token, set_token
from tp_auth_serverside.db.memorydb.refresh import set_restrict_refresh
from tp_auth_serverside.utilities.jwt_util import JWTUtil


class AuthenticationHandler:
    async def authenticate(self, response: Response, user_id: str, payload: UserInfoSchema):
        jwt_util = JWTUtil()
        jwt_token = jwt_util.encode(payload.model_dump())
        token = await set_token(user_id, jwt_token)
        await set_restrict_refresh(user_id, token)
        response.set_cookie(key="user_id", value=user_id, httponly=True, secure=True, samesite="strict")
        response.set_cookie(key="access_token", value=token, httponly=True, secure=True, samesite="strict")
        return token

    async def revoke_authentication(self, response: Response, user_id: str, token: str):
        await revoke_token(user_id, token)
        response.delete_cookie(key="user_id")
        response.delete_cookie(key="access_token")
