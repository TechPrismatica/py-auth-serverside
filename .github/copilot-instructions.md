# tp-auth-serverside - GitHub Copilot Instructions

**Python package for server-side authentication and authorization with memory database session storage, supporting JWT tokens, FastAPI integration, and gRPC services.**

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Environment Manager:
- **Package Manager**: Uses `uv` for dependency and virtual environment management
- **Activate Environment**: Always use `source .venv/bin/activate` before running any Python commands
- **Install Dependencies**: `uv pip install -e .` or `pip install -e .` (within activated venv)
- **All Python/pip commands must be run within activated venv**

### Bootstrap, Build, and Test Repository:
- `source .venv/bin/activate` -- activate the uv-managed virtual environment FIRST
- `pip install -e .` -- installs the package in development mode. NEVER CANCEL: Takes 10-60 seconds, may timeout due to network issues. Set timeout to 120+ seconds (extra margin for slow mirrors or network issues).
- `pip install coverage pre-commit pytest pytest-cov pytest-dotenv ruff grpcio-tools` -- installs development dependencies. NEVER CANCEL: Takes 30-120 seconds. Set timeout to 180+ seconds (extra margin for slow mirrors or network issues).
- `python -m pytest tests/ -v` -- runs unit tests (when tests are available)
- `ruff check .` -- runs linting (takes ~0.01 seconds)
- `ruff format --check .` -- checks code formatting (takes ~0.01 seconds)

### Environment Configuration:
- Create `.env` file with `DB_URL=redis://localhost:6379/0` for basic testing
- Package requires `DB_URL` environment variable to be set at runtime for memory database connectivity
- Additional required environment variables: `SECRET_KEY` (for HS256) or `PUBLIC_KEY`/`PRIVATE_KEY` (for RS256)
- Supported database URLs: `redis://`, `memcached://`, `dragonfly://`, `valkey://`
- Optional environment variables: `ALGORITHM`, `ISSUER`, `LEEWAY`, `EXPIRY`, `AUTHORIZATION_SERVER`, `AUTH_SCOPES`

### Run Integration Tests with Real Database:
- Start Redis: `docker run -d --name test-redis -p 6379:6379 redis:7-alpine` (NEVER CANCEL: Takes 30-60 seconds for first download)
- Wait for startup: `sleep 5`
- Run integration tests: `DB_URL=redis://localhost:6379/0 SECRET_KEY=test_secret python -c "from tp_auth_serverside import JWTUtil; print('Auth integration test passed')"` (basic JWT functionality test)
- Clean up: `docker stop test-redis && docker rm test-redis`

## Validation Scenarios

### Always Test After Making Changes:
1. **Import Test**: `DB_URL=redis://localhost:6379/0 SECRET_KEY=test_secret python -c "from tp_auth_serverside import JWTUtil, AuthValidator; print('Import successful')"`
2. **Basic JWT Functionality Test** (requires Redis running):
   ```bash
   DB_URL=redis://localhost:6379/0 SECRET_KEY=test_secret python -c "
   from tp_auth_serverside import JWTUtil
   jwt_util = JWTUtil()
   payload = {'user_id': 'test', 'username': 'testuser'}
   token = jwt_util.encode(payload)
   decoded = jwt_util.decode(token)
   assert decoded['user_id'] == 'test'
   print('JWT Validation PASSED')
   "
   ```
3. **Run Full Test Suite**: `python -m pytest tests/ -v --cov=src --cov-report=term-missing` (when tests are available)
4. **Linting**: `ruff check . && ruff format --check .`

### Manual Testing Requirements:
- ALWAYS test basic JWT token creation and validation after code changes
- Test with different algorithms (HS256, RS256) by changing environment variables
- Verify authentication flows work with FastAPI integration
- Test memory database session storage functionality
- Test error handling with invalid database URLs or unreachable servers

## Common Tasks

### Repository Structure:
```
tp-auth-serverside/
├── .github/workflows/     # CI/CD pipelines
├── src/tp_auth_serverside/ # Main package source
│   ├── __init__.py       # Main exports (JWTUtil, AuthValidator, etc.)
│   ├── config.py         # Environment configuration and settings
│   ├── py.typed          # Type hints marker
│   ├── auth/             # Authentication and authorization modules
│   │   ├── __init__.py
│   │   ├── auth_validator.py   # JWT token validation
│   │   ├── requestor.py        # HTTP request handling with auth
│   │   ├── schemas.py          # Pydantic schemas
│   │   └── user_specs.py       # User information specifications
│   ├── core/             # Core FastAPI and handler modules
│   │   ├── __init__.py
│   │   ├── fastapi_configurer.py  # FastAPI app configuration
│   │   └── handler/
│   │       ├── __init__.py
│   │       ├── authentication_handler.py  # Auth flow handlers
│   │       └── refresh_handler.py         # Token refresh gRPC service
│   ├── db/               # Database operations
│   │   ├── __init__.py
│   │   └── memorydb/
│   │       ├── __init__.py
│   │       ├── login.py        # Login session storage
│   │       └── refresh.py      # Refresh token restrictions
│   ├── pb/               # Protocol Buffer generated files
│   │   ├── refresh_pb2.py      # Generated protobuf classes
│   │   └── refresh_pb2_grpc.py # Generated gRPC service stubs
│   └── utilities/        # Utility modules
│       ├── __init__.py
│       └── jwt_util.py         # JWT token utilities
├── protos/               # Protocol Buffer definitions
│   └── refresh.proto     # gRPC refresh service definition
├── tests/                # Test files (when available)
├── pyproject.toml        # Project configuration
└── README.md            # Documentation
```

### Key Files to Check After Changes:
- Always verify `src/tp_auth_serverside/__init__.py` after changing main exports
- Check `src/tp_auth_serverside/config.py` after modifying configuration handling
- Update `src/tp_auth_serverside/utilities/jwt_util.py` when changing JWT functionality
- Verify `src/tp_auth_serverside/auth/auth_validator.py` after authentication changes
- Test `src/tp_auth_serverside/core/handler/authentication_handler.py` for auth flow changes
- Check `src/tp_auth_serverside/db/memorydb/` modules for session storage changes
- Regenerate protobuf files in `src/tp_auth_serverside/pb/` when updating `protos/refresh.proto`
- Update tests in `tests/` when adding new functionality
- Run integration tests with real database for full functionality verification

### Development Dependencies:
- **Testing**: pytest, pytest-cov, pytest-dotenv, coverage
- **Linting**: ruff (replaces black, flake8, isort)
- **Git hooks**: pre-commit
- **gRPC Tools**: grpcio-tools (for protobuf compilation)
- **Type checking**: Built into package with py.typed marker
- **Core Dependencies**: FastAPI, PyJWT, pydantic, mem-db-utils, grpcio

### Build and Package:
- `python -m build` -- builds distribution packages. NEVER CANCEL: May fail due to network timeouts depending on the configured build backend and network environment (see `pyproject.toml` for the backend in use). Consider this command unreliable in constrained network environments.
- Package metadata in `pyproject.toml`
- Uses standard Python packaging; the build backend is specified in `pyproject.toml` (may require network access to a custom PyPI index depending on backend).
- **Note**: Package installation works fine, but building from source may be problematic due to external dependencies

### gRPC and Protocol Buffer Development:
- **Protobuf Compilation**: `python -m grpc_tools.protoc --proto_path=protos --python_out=src/tp_auth_serverside/pb --grpc_python_out=src/tp_auth_serverside/pb protos/refresh.proto`
- **After Generation**: Manually fix the import in `refresh_pb2_grpc.py` to use absolute import: `from tp_auth_serverside.pb import refresh_pb2 as refresh__pb2`
- **Generated Files**: Located in `src/tp_auth_serverside/pb/` (refresh_pb2.py, refresh_pb2_grpc.py)
- **Service Implementation**: `RefreshHandler` class in `src/tp_auth_serverside/core/handler/refresh_handler.py`
- **Testing gRPC**: Requires starting both Redis and gRPC server for integration tests
- **Proto Schema**: `protos/refresh.proto` defines the RefreshService interface
- **No External Proto Dependencies**: Package uses custom `RefreshResponse` message instead of `google.protobuf.Empty` to avoid external dependencies

## Database Types and Testing

### Supported Database Types:
- **Redis**: `redis://localhost:6379/0` (most common, full functionality)
- **Memcached**: `memcached://localhost:11211` (basic key-value operations)
- **Dragonfly**: `dragonfly://localhost:6380` (Redis-compatible)
- **Valkey**: `valkey://localhost:6381` (Redis-compatible)

### Database-Specific Testing:
- **Redis/Dragonfly/Valkey**: Support database selection (`db` parameter), ping, set/get/delete
- **Memcached**: Basic connection only, no database selection
- **Redis Sentinel**: Requires `REDIS_CONNECTION_TYPE=sentinel` and `REDIS_MASTER_SERVICE` environment variables

### Setting up Test Databases with Docker:
- Redis: `docker run -d --name test-redis -p 6379:6379 redis:7-alpine`
- Memcached: `docker run -d --name test-memcached -p 11211:11211 memcached:1.6-alpine`
- Dragonfly: `docker run -d --name test-dragonfly -p 6380:6380 docker.dragonflydb.io/dragonflydb/dragonfly`

## CI/CD Pipeline (.github/workflows)

### Linter Pipeline (linter.yaml):
- Runs on pull requests
- Uses `chartboost/ruff-action@v1` for linting and format checking
- ALWAYS run `ruff check .` and `ruff format --check .` before committing

### Package Publishing (publish_package.yaml):
- Triggers on git tags
- Builds with `python -m build`
- Publishes to PyPI
- Creates GitHub releases with sigstore signatures

## Critical Notes

### Environment Variable Loading:
- Package uses `pydantic-settings` with `python-dotenv` integration
- Environment variables are loaded from `.env` files automatically
- Configuration is validated at import time, not lazily
- Missing `DB_URL` will cause import failure with ValidationError

### Error Handling:
- Import failures occur when `DB_URL` is missing or invalid protocol
- Connection failures in integration tests are skipped (pytest.skip)
- Invalid database numbers may or may not raise exceptions depending on database type

### Memory and Performance:
- MemDBConnector uses `__slots__` for memory efficiency
- Connection objects are created per call to `connect()`
- No connection pooling implemented in base connector
- Timeouts configurable via `DB_TIMEOUT` environment variable (default: 30 seconds)

## Troubleshooting

### Common Issues:
1. **Import Error**: Ensure `DB_URL` environment variable is set
2. **Test Failures**: Start appropriate database container first
3. **Linting Failures**: Run `ruff format .` to auto-fix formatting issues
4. **Missing Dependencies**: Run `pip install -e .` to reinstall package
5. **Network Timeouts**: Package uses custom PyPI index (pypi.prismatica.in) which may be unreachable. pip install and python -m build commands may timeout.

### Network Dependencies:
- Package depends on custom PyPI index at pypi.prismatica.in
- Build commands may fail with network timeouts in restricted environments
- Runtime functionality works fine once dependencies are installed
- Consider using pre-installed environments or alternative package sources if network issues persist

### Database Connection Issues:
- Check if database container is running: `docker ps`
- Test connection manually: `docker exec -it test-redis redis-cli ping`
- Verify port availability: `netstat -tlnp | grep 6379`
- Check firewall settings if running on remote host
