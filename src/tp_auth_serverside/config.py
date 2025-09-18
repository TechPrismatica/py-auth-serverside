from enum import StrEnum
from typing import Any, Optional

from fastapi.security import OAuth2PasswordBearer
from pydantic import BeforeValidator, Field, model_validator
from pydantic_settings import BaseSettings
from typing_extensions import Annotated


def options_decoder(v):
    if isinstance(v, str):
        return v.split(",")
    return v


OptionsType = Annotated[Any, BeforeValidator(options_decoder)]


class SupportedAlgorithms(StrEnum):
    HS256 = "HS256"
    RS256 = "RS256"


class _Service(BaseSettings):
    docs_url: Optional[str] = Field("/docs", env="DOCS_URL")
    redoc_url: Optional[str] = Field("/redoc", env="REDOC_URL")
    openapi_url: Optional[str] = Field("/openapi.json", env="OPENAPI_URL")
    enable_cors: Optional[bool] = True
    cors_urls: OptionsType = ["*.prismatica.in"]
    cors_allow_credentials: bool = True
    cors_allow_methods: OptionsType = ["GET", "POST", "DELETE", "PUT", "OPTIONS", "PATCH"]
    cors_allow_headers: OptionsType = ["*"]


class _Database(BaseSettings):
    login_redis_db: Optional[int] = 9
    refresh_restrict_db: Optional[int] = 8


class _Secrets(BaseSettings):
    public_key: Optional[str] = Field(None, env="PUBLIC_KEY")
    private_key: Optional[str] = Field(None, env="PRIVATE_KEY")
    secret_key: Optional[str] = Field(None, env="SECRET_KEY")
    algorithm: Optional[SupportedAlgorithms] = Field(default=SupportedAlgorithms.HS256, env="ALGORITHM")
    issuer: Optional[str] = Field("prismaticain", env="ISSUER")
    leeway: Optional[int] = Field(10, env="LEEWAY")
    expiry: Optional[int] = Field(1440, env="EXPIRY")
    authorization_server: Optional[bool] = Field(False, env="AUTHORIZATION_SERVER")
    scopes: Optional[dict] = Field(None, env="AUTH_SCOPES")
    token_url: Optional[str] = Field("/token", env="TOKEN_URL")
    refresh_url: Optional[str] = Field("/refresh", env="REFRESH_URL")
    refresh_restrict_minutes: Optional[int] = Field(2, env="REFRESH_RESTRICT_MINUTES")

    @model_validator(mode="before")
    def check_secrets(cls, values) -> dict:
        if values["algorithm"] == SupportedAlgorithms.RS256:
            import base64

            if not values.get("public_key"):
                raise ValueError("Public must be provided for RS256 algorithm")
            public_bytes = values["public_key"].encode("utf-8")
            values["public_key"] = base64.b64decode(public_bytes).decode("utf-8")
            if values["authorization_server"] and not values["private_key"]:
                raise ValueError("Private key must be provided for RS256 algorithm when used as authorization server")
            private_bytes = values.get("private_key")
            if private_bytes:
                private_bytes = private_bytes.encode("utf-8")
                values["private_key"] = base64.b64decode(private_bytes).decode("utf-8")
        elif values["algorithm"] == SupportedAlgorithms.HS256:
            if not values.get("secret_key"):
                raise ValueError("Secret key must be provided for HS256 algorithm")
        return values


Secrets = _Secrets()
Service = _Service()
Database = _Database()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=Secrets.token_url, scopes=Secrets.scopes)

__all__ = ["Secrets", "SupportedAlgorithms", "Database", "Service", "oauth2_scheme"]
