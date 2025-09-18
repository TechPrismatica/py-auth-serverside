import grpc
import jwt
from fastapi import Cookie, Depends, Header, HTTPException, status
from fastapi.security import SecurityScopes
from typing_extensions import Annotated

from tp_auth_serverside.auth.user_specs import UserInfoSchema
from tp_auth_serverside.config import Secrets, oauth2_scheme
from tp_auth_serverside.db.memorydb.login import get_token
from tp_auth_serverside.pb import refresh_pb2
from tp_auth_serverside.pb.refresh_pb2_grpc import RefreshServiceStub
from tp_auth_serverside.utilities.jwt_util import JWTUtil


class AuthValidator:
    def __init__(self, jwt_util: JWTUtil = None) -> None:
        self.jwt_utils = jwt_util or JWTUtil()

    async def _trigger_refresh(self, user_id: str, token: str) -> None:
        try:
            async with grpc.aio.insecure_channel(Secrets.refresh_url) as channel:
                stub = RefreshServiceStub(channel)
                request = refresh_pb2.RefreshRequest(user_id=user_id, token=token)
                await stub.RefreshToken(request)
        except Exception:
            pass

    async def __call__(
        self,
        security_scopes: SecurityScopes,
        token: Annotated[str, Depends(oauth2_scheme)],
        user_id: Annotated[str, Cookie],
        refresh: Annotated[bool | True, Header] = True,
    ) -> UserInfoSchema:
        if security_scopes.scopes:
            authenticate_value = f"Bearer scope={security_scopes.scope_str}"
        else:
            authenticate_value = "Bearer"
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )
        try:
            jwt_token = await get_token(user_id, token)
            if not jwt_token:
                raise credentials_exception
            payload = self.jwt_utils.decode(jwt_token)
            if payload.get("token_type") != "access":
                raise credentials_exception
            user_info = UserInfoSchema(**payload)
            available_scopes = user_info.scopes
            if refresh:
                await self._trigger_refresh(user_id, token)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.InvalidSignatureError):
            raise credentials_exception
        for scope in security_scopes.scopes:
            if scope not in available_scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )
        return user_info


AuthValidatorInstance = AuthValidator()
UserInfo = Annotated[UserInfoSchema, Depends(AuthValidatorInstance)]

__all__ = ["AuthValidator", "UserInfo", "AuthValidatorInstance"]
