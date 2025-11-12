import logging
from concurrent import futures
from contextlib import asynccontextmanager
from typing import Callable, Optional, Tuple

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import APIRouter, Cookie, Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing_extensions import Annotated

from tp_auth_serverside.auth.auth_validator import AuthValidatorInstance
from tp_auth_serverside.auth.schemas import Token
from tp_auth_serverside.auth.user_specs import UserInfoSchema
from tp_auth_serverside.config import Secrets, Service
from tp_auth_serverside.core.handler.authentication_handler import AuthenticationHandler


class FastAPIConfig(BaseModel):
    title: str
    version: str
    description: str
    root_path: str
    docs_url: str = Service.docs_url
    redoc_url: str = Service.redoc_url
    openapi_url: str = Service.openapi_url
    tags_metadata: Optional[list[dict]] = None
    exception_handlers: Optional[dict] = None
    lifespan: Optional[Callable] = None


class StatusResponse(BaseModel):
    status: int = 200


def get_custom_api(app: FastAPI, app_config: FastAPIConfig, disable_operation_default: bool) -> Callable:
    if not disable_operation_default:
        app_config.tags_metadata = app_config.tags_metadata or []
        app_config.tags_metadata.append(
            {
                "name": "Operational Services",
                "description": "The **Operational Services** tag groups all the endpoints related to operational services provided by the TechPrismatica platform.",
            }
        )

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app_config.title,
            version=app_config.version,
            description=app_config.description,
            routes=app.routes,
            servers=app.servers,
        )
        openapi_schema["tags"] = app_config.tags_metadata
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return custom_openapi


def add_health_check(app: FastAPI, health_check_routine: Callable = None, asynced: bool = False) -> FastAPI:
    @app.get(
        "/api/healthcheck",
        name="Health Check",
        tags=["Operational Services"],
        response_model=StatusResponse,
    )
    async def ping():
        """
        This function sends a ping request to the server and returns a StatusResponse object.
        """
        if health_check_routine:
            if asynced:
                status = await health_check_routine()
            else:
                status = health_check_routine()
            if not status:
                return StatusResponse(status=500)
        return StatusResponse()

    return app


def add_security(app: FastAPI, routers: list[APIRouter]) -> FastAPI:
    [app.include_router(router, dependencies=[Depends(AuthValidatorInstance)]) for router in routers]
    return app


def add_cors(app: FastAPI) -> FastAPI:
    if Service.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=Service.cors_urls,
            allow_credentials=Service.cors_allow_credentials,
            allow_methods=Service.cors_allow_methods,
            allow_headers=Service.cors_allow_headers,
        )
    return app


def add_token_route(app: FastAPI, handler: Callable, asynced: bool = False, dependency=None) -> FastAPI:
    @app.post("/token", response_model=Token, tags=["Authentication"])
    async def token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        request: Request,
        response: Response,
        dependency=Depends(dependency),
    ) -> Token:
        if asynced:
            user_id, payload = await handler(form_data, request, response, dependency)
        else:
            user_id, payload = handler(form_data, request, response, dependency)
        token = await AuthenticationHandler().authenticate(response, user_id, payload)
        return Token(user_id=user_id, token=token)

    return app


def add_logout_route(app: FastAPI, handler: Callable = None, asynced: bool = False) -> FastAPI:
    @app.post("/logout", response_model=StatusResponse, tags=["Authentication"])
    async def logout(
        request: Request,
        response: Response,
        access_token: Annotated[str, Cookie()],
        user: Annotated[UserInfoSchema, Depends(AuthValidatorInstance)],
    ) -> StatusResponse:
        if handler is not None:
            if asynced:
                await handler(request, response, user.user_id, user)
            else:
                handler(request, response, user.user_id, user)
        await AuthenticationHandler().revoke_authentication(response, user.user_id, access_token)
        return StatusResponse()

    return app


async def start_refresh_service():
    """
    Start the gRPC refresh service as a background task.
    Returns the server instance for lifecycle management.
    """
    import grpc

    from tp_auth_serverside.core.handler.refresh_handler import RefreshHandler
    from tp_auth_serverside.pb import refresh_pb2_grpc

    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=2))
    refresh_pb2_grpc.add_RefreshServiceServicer_to_server(RefreshHandler(), server)
    server.add_insecure_port(Secrets.refresh_url)
    logging.info(f"Starting refresh service on {Secrets.refresh_url}")
    await server.start()
    logging.info("Refresh service started")
    return server


def generate_fastapi_app(
    app_config: FastAPIConfig,
    routers: list[APIRouter],
    disable_operation_default: bool = False,
    token_route_handler: Optional[Callable | Tuple[Callable, bool]] = None,
    logout_route_handler: Optional[Callable | Tuple[Callable, bool]] = None,
    health_check_routine: Optional[Callable | Tuple[Callable, bool]] = None,
) -> FastAPI:
    # Create lifespan context manager for gRPC server lifecycle
    @asynccontextmanager
    async def lifespan_with_grpc(app: FastAPI):
        grpc_server = None
        # Startup: Start the gRPC refresh service
        if Secrets.authorization_server:
            logging.info("Initializing gRPC refresh service...")
            grpc_server = await start_refresh_service()

        # Call user-provided lifespan if exists
        if app_config.lifespan:
            async with app_config.lifespan(app):
                yield
        else:
            yield

        # Shutdown: Stop the gRPC server gracefully
        if grpc_server:
            logging.info("Shutting down gRPC refresh service...")
            await grpc_server.stop(grace=5)
            logging.info("gRPC refresh service stopped")

    # Use the combined lifespan if authorization_server is enabled
    final_lifespan = lifespan_with_grpc if Secrets.authorization_server else app_config.lifespan

    app = FastAPI(
        title=app_config.title,
        version=app_config.version,
        description=app_config.description,
        root_path=app_config.root_path,
        openapi_url=app_config.openapi_url,
        docs_url=app_config.docs_url,
        redoc_url=app_config.redoc_url,
        lifespan=final_lifespan,
        exception_handlers=app_config.exception_handlers,
        default_response_class=ORJSONResponse,
    )
    app.openapi = get_custom_api(app, app_config, disable_operation_default)
    if isinstance(health_check_routine, tuple):
        app = add_health_check(app, health_check_routine[0], health_check_routine[1])
    else:
        app = add_health_check(app)
    app = add_security(app, routers)
    app = add_cors(app)
    if token_route_handler:
        if isinstance(token_route_handler, tuple):
            app = add_token_route(app, *token_route_handler)
        else:
            app = add_token_route(app, token_route_handler)
    if logout_route_handler:
        if isinstance(logout_route_handler, tuple):
            app = add_logout_route(app, *logout_route_handler)
        else:
            app = add_logout_route(app, logout_route_handler)
    else:
        app = add_logout_route(app)
    app.add_middleware(CorrelationIdMiddleware)
    return app


__all__ = [
    "FastAPIConfig",
    "generate_fastapi_app",
]
