# TP Auth Serverside🔐

TP Auth Serverside is a comprehensive server-side authentication and authorization solution designed specifically for TechPrismatica projects. It leverages FastAPI, Pydantic, and in-memory database storage to provide a secure, scalable, and easy-to-integrate authentication system. With support for JWT-based access tokens, Redis-backed session storage, gRPC refresh services, and environment variable configurations for seamless deployment, TP Auth Serverside aims to streamline the security aspects of your applications.

This documentation covers everything from setting up environment variables, configuring memory databases, installing the package, to integrating TP Auth Serverside into your authorization and resource servers. Whether you're looking to secure your APIs, implement role-based access control (RBAC), manage user authentication flows with persistent session storage, or implement token refresh mechanisms, TP Auth Serverside provides the tools and guidance necessary to achieve a robust security posture.

## Features ✨

- **JWT-Based Authentication**: Utilize JSON Web Tokens (JWT) for secure, stateless authentication across your services.
- **Memory Database Session Storage**: Store and manage session tokens in Redis-compatible memory databases for enhanced performance and security.
- **Token Refresh Management**: Implement sophisticated token refresh mechanisms with restrictions to prevent replay attacks.
- **gRPC Refresh Service**: Built-in gRPC service for efficient token refresh operations across microservices.
- **Environment Variable Configurations**: Easily configure your application's security settings through environment variables, making it adaptable to different deployment environments.
- **FastAPI Integration**: Seamlessly integrate with FastAPI applications, allowing for straightforward implementation of authentication and authorization mechanisms.
- **Role-Based Access Control (RBAC)**: Implement fine-grained access control to manage user permissions and secure your endpoints.
- **Customizable Authentication Flows**: Define custom methods for token creation, refresh, and user authentication to fit your application's specific needs.
- **Enhanced Security**: Token restriction mechanisms prevent unauthorized token reuse and provide additional security layers.

## Getting Started 🚀

To get started with TP Auth Serverside, follow the sections below on installation, setting up environment variables, configuring memory databases, and integrating TP Auth Serverside into your FastAPI applications. Detailed examples and configurations are provided to ensure a smooth setup process.

For a complete guide on how to use TP Auth Serverside in your projects, refer to the [Table of Contents 📑](#table-of-contents-).

We hope TP Auth Serverside enhances the security of your TechPrismatica projects with its robust set of features, memory database integration, and ease of use. Happy coding!

## Table of Contents 📑

- [TP Auth Serverside🔐](#tp-auth-serverside)
  - [Features ✨](#features-)
  - [Getting Started 🚀](#getting-started-)
  - [Table of Contents 📑](#table-of-contents-)
  - [Environment Variable Configurations 🛠️](#environment-variable-configurations-️)
  - [Installation 💾](#installation-)
    - [Dependencies](#dependencies)
  - [Memory Database Configuration 🗄️](#memory-database-configuration-️)
    - [Supported Databases](#supported-databases)
    - [Database Setup](#database-setup)
    - [Database Configuration Variables](#database-configuration-variables)
    - [Database Usage](#database-usage)
  - [Usage 📋](#usage-)
    - [Using in Authorization Servers](#using-in-authorization-servers)
      - [Setting ENV Configuration for Authorization Server](#setting-env-configuration-for-authorization-server)
      - [Defining Access Token Creation Method](#defining-access-token-creation-method)
      - [Registering defined methods with fastapi generator](#registering-defined-methods-with-fastapi-generator)
    - [Using in Resource Servers](#using-in-resource-servers)
      - [Setting ENV Configuration for Resource Server](#setting-env-configuration-for-resource-server)
      - [Getting User Details](#getting-user-details)
      - [Adding RBAC to Route](#adding-rbac-to-route)
      - [Communication to other resource servers](#communication-to-other-resource-servers)
  - [gRPC Refresh Service 🔄](#grpc-refresh-service-)
  - [Authors 👩‍💻👨‍💻](#authors-)
  - [Authors 👩‍💻👨‍💻](#authors-)

## Environment Variable Configurations 🛠️

|SNo.|Variable Name|Required|Default|Description|
|---|-------------|--------|-------|-----------|
|1|DOCS_URL|❌|/docs|FastAPI docs endpoint URL|
|2|REDOC_URL|❌|/redoc|ReDoc documentation endpoint URL|
|3|OPENAPI_URL|❌|/openapi.json|OpenAPI specification endpoint URL|
|4|PUBLIC_KEY|❌|None|Base64 encoded public key for RS256 algorithm|
|5|PRIVATE_KEY|❌|None|Base64 encoded private key for RS256 algorithm|
|6|SECRET_KEY|❌|None|Secret key for HS256 algorithm|
|7|ALGORITHM|❌|HS256|JWT signing algorithm (HS256 or RS256)|
|8|ISSUER|❌|prismaticain|JWT token issuer|
|9|LEEWAY|❌|10|Acceptable time gap between client & server in minutes|
|10|EXPIRY|❌|1440|Expiry time for access token in minutes|
|11|AUTHORIZATION_SERVER|❌|False|Whether this service acts as authorization server|
|12|AUTH_SCOPES|❌|None|Available authorization scopes in application|
|13|TOKEN_URL|❌|/token|Token endpoint URL|
|14|REFRESH_URL|❌|/refresh|Token refresh endpoint URL|
|15|REFRESH_RESTRICT_MINUTES|❌|2|Time in minutes to restrict token refresh after use|
|16|LOGIN_REDIS_DB|❌|9|Redis database number for login token storage|
|17|REFRESH_RESTRICT_DB|❌|8|Redis database number for refresh restriction storage|
|18|CORS_URLS|❌|["*.prismatica.in"]|Allowed CORS origin URLs|
|19|CORS_ALLOW_CREDENTIALS|✅|True|Allow credentials in CORS requests|
|20|CORS_ALLOW_METHODS|❌|["GET", "POST", "DELETE", "PUT", "OPTIONS", "PATCH"]|Allowed HTTP methods for CORS|
|21|CORS_ALLOW_HEADERS|❌|["*"]|Allowed headers for CORS|
|22|ENABLE_CORS|❌|True|Enable CORS middleware|
|23|DB_URL|✅|None|Memory database connection URL (required for mem-db-utils)|

Note: For `CORS_URLS`, `CORS_ALLOW_METHODS`, and `CORS_ALLOW_HEADERS`, the default values are lists. Ensure to format them appropriately in your environment configuration. The `DB_URL` variable is required for memory database connectivity and should follow the format supported by mem-db-utils (e.g., redis://localhost:6379/0).

## Installation 💾

```bash
pip install tp-auth-serverside
```

Note: tp-auth-serverside is only available through PyPi server of TechPrismatica, Please contact Organisation maintainers/Devops team for PyPi server creds and URL.

### Dependencies

This package requires the following key dependencies:
- `mem-db-utils>=0.2.0` - For memory database connectivity (Redis, Memcached, Dragonfly, Valkey)
- `fastapi>=0.116.1` - Web framework
- `pyjwt>=2.10.1` - JWT token handling
- `grpcio>=1.75.0` - gRPC support for refresh services
- `pydantic>=2.11.7` - Data validation

## Memory Database Configuration 🗄️

TP Auth Serverside uses memory databases for session token storage and refresh token restriction management. The package supports Redis-compatible databases through the `mem-db-utils` library.

### Supported Databases

- **Redis**: Most common, full functionality support
- **Dragonfly**: Redis-compatible with enhanced performance
- **Valkey**: Redis-compatible alternative
- **Memcached**: Basic key-value operations

### Database Setup

1. **Redis (Recommended)**:
   ```bash
   # Using Docker
   docker run -d --name auth-redis -p 6379:6379 redis:7-alpine

   # Set environment variable
   export DB_URL=redis://localhost:6379/0
   ```

2. **Dragonfly**:
   ```bash
   # Using Docker
   docker run -d --name auth-dragonfly -p 6380:6380 docker.dragonflydb.io/dragonflydb/dragonfly

   # Set environment variable
   export DB_URL=dragonfly://localhost:6380/0
   ```

### Database Configuration Variables

- `DB_URL`: Memory database connection URL (required)
- `LOGIN_REDIS_DB`: Database number for login token storage (default: 9)
- `REFRESH_RESTRICT_DB`: Database number for refresh restriction storage (default: 8)

### Database Usage

The package automatically creates two separate database connections:
- **Login DB**: Stores user session tokens with expiration
- **Refresh Restrict DB**: Manages token refresh restrictions to prevent replay attacks

## Usage 📋

### Using in Authorization Servers

TP-Auth can be used to create the authorization server.

#### Setting ENV Configuration for Authorization Server

```env
# Memory Database Configuration (Required)
DB_URL = redis://localhost:6379/0

# Let's Utility know this microservice is a authorization server.
AUTHORIZATION_SERVER = True

# Domain or Company Name.
ISSUER = prismaticain

# Acceptable time gap between client & server in mins.
LEEWAY = 10

# Expiry time for access token in mins.
EXPIRY = 1440

# Time in minutes to restrict token refresh after use (prevents replay attacks).
REFRESH_RESTRICT_MINUTES = 2

# Available authorization scopes in application. If not provided ignores scope checks.
AUTH_SCOPES = {"read": "Read Access", "write": "Write Access"}

# Database configuration for session storage
LOGIN_REDIS_DB = 9
REFRESH_RESTRICT_DB = 8

# Cors configurations.
CORS_URLS = ["*.prismatica.in"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "DELETE", "PUT", "OPTIONS", "PATCH"]
CORS_ALLOW_HEADERS = ["*"]
ENABLE_CORS = True

# If Algorithm is set to HS256.
SECRET_KEY = SomeSecret

# If Algorithm is set to RS256.
PUBLIC_KEY = Base64 Encoded public key
PRIVATE_KEY = Base64 Encoded private key
```

#### Defining Access Token Creation Method

To facilitate secure and efficient access token creation, our method meticulously requires the specification of three critical parameters: **OAuth2PasswordRequestForm**, **Request**, and **Response**. These parameters are essential for accurately processing authentication requests, ensuring the integrity of the authentication flow, and providing a seamless user experience.
It should return a Token object.

**Note**: The new serverside implementation automatically handles session storage in memory databases and provides enhanced security features.

Example:

```python
from fastapi import Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from tp_auth_serverside import JWTUtil, Token

def token_creator(creds: OAuth2PasswordRequestForm, request: Request, response: Response) -> Token:
    payload = {
        "user_id": "user_099",
        "scopes": ["user:read", "user:write"],
        "username": "Admin",
        "issued_to": request.client.host,
    }
    return payload["user_id"], payload
```

#### Registering defined methods with fastapi generator

```python
from fastapi import APIRouter
from tp_auth_serverside import FastAPIConfig, generate_fastapi_app

test_route = APIRouter()

app_config = FastAPIConfig(
    title="Test API",
    version="0.1.0",
    description="Test API for TP Auth Serverside",
    root_path="",
)

app = generate_fastapi_app(
    app_config=app_config,
    routers=[test_route],
    token_route_handler=token_creator,
)
```

### Using in Resource Servers

TP Auth Serverside can be used in resource servers to authenticate user and provide resources.

#### Setting ENV Configuration for Resource Server

```env
# Memory Database Configuration (Required for session validation)
DB_URL = redis://localhost:6379/0

# Available authorization scopes in application. If not provided ignores scope checks.
AUTH_SCOPES = {"read": "Read Access", "write": "Write Access"}

# Database configuration for session storage
LOGIN_REDIS_DB = 9
REFRESH_RESTRICT_DB = 8

# If Algorithm is set to HS256.
SECRET_KEY = SomeSecret

# If Algorithm is set to RS256.
PUBLIC_KEY = Base64 Encoded public key
```

#### Getting User Details

```python
from tp_auth_serverside import UserInfo

@test_route.get("/user")
def get_user(user: UserInfo):
    return f"Hello {user.username}"
```

#### Adding RBAC to Route

```python
from fastapi import Security
from tp_auth_serverside import AuthValidatorInstance, UserInfoSchema

@test_route.get("/user")
def get_user(user: Annotated[UserInfoSchema, Security(AuthValidatorInstance, scopes=["user:write"])]):
    return f"Hello {user.username}"
```

#### Communication to other resource servers

```python
from tp_auth_serverside import TPRequestorInstance

@test_route.get("/forwarded")
def get_forwarded(requestor: TPRequestorInstance):
    resp = requestor.get(url="http://localhost:8001/user")
    return resp.text
```

## gRPC Refresh Service 🔄

TP Auth Serverside includes a built-in gRPC service for efficient token refresh operations across microservices. This service provides a high-performance alternative to HTTP-based refresh mechanisms.
The Service works automatically and doesn't require any intervention from user side.

## Authors 👩‍💻👨‍💻

- [<img src="https://avatars.githubusercontent.com/faizanazim11" width="40" height="40" style="border-radius:50%; vertical-align: middle;" alt="GitHub"/>](https://github.com/faizanazim11) [Faizan Azim](mailto:faizanazim11@gmail.com) - [<img src="https://github.githubassets.com/images/icons/emoji/octocat.png" width="40" height="40" style="vertical-align: middle;" alt="GitHub"/>](https://github.com/faizanazim11)
