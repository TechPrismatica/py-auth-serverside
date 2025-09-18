from typing import Any, override

import httpx
from fastapi import Depends
from typing_extensions import Annotated

from tp_auth_serverside.config import oauth2_scheme


class TPRequestor:
    """A class to handle requests to the TP Resource Servers.

    Supports synchronous and asynchronous requests.
    Uses the `httpx` library to make requests.
    For all available parameters, see the `httpx` documentation.

    Supports the following methods:
    - delete
    - get
    - patch
    - post
    - put
    - request
    - aio_delete
    - aio_get
    - aio_patch
    - aio_post
    - aio_put
    - aio_request

    """

    def __init__(self, token: Annotated[str, Depends(oauth2_scheme)]) -> None:
        self.__dict__["_token"] = token

    @property
    def token(self):
        return self._token

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent setting attributes"""
        raise AttributeError("Cannot set attributes")

    def _update_headers(self, headers: dict) -> dict:
        headers.update({"Authorization": f"Bearer {self.token}"})
        headers.update({"refresh": "false"})
        return headers

    def delete(self, **kwargs) -> httpx.Response:
        headers = kwargs.pop("headers", {})
        self._update_headers(headers)
        with httpx.Client(
            headers=headers, cookies=kwargs.pop("cookies", None), verify=kwargs.pop("verify", False)
        ) as client:
            return client.delete(**kwargs)

    def get(self, **kwargs) -> httpx.Response:
        headers = kwargs.pop("headers", {})
        self._update_headers(headers)
        with httpx.Client(
            headers=headers, cookies=kwargs.pop("cookies", None), verify=kwargs.pop("verify", False)
        ) as client:
            return client.get(**kwargs)

    def patch(self, **kwargs) -> httpx.Response:
        headers = kwargs.pop("headers", {})
        self._update_headers(headers)
        with httpx.Client(
            headers=headers, cookies=kwargs.pop("cookies", None), verify=kwargs.pop("verify", False)
        ) as client:
            return client.patch(**kwargs)

    def post(self, **kwargs) -> httpx.Response:
        headers = kwargs.pop("headers", {})
        self._update_headers(headers)
        with httpx.Client(
            headers=headers, cookies=kwargs.pop("cookies", None), verify=kwargs.pop("verify", False)
        ) as client:
            return client.post(**kwargs)

    def put(self, **kwargs) -> httpx.Response:
        headers = kwargs.pop("headers", {})
        self._update_headers(headers)
        with httpx.Client(
            headers=headers, cookies=kwargs.pop("cookies", None), verify=kwargs.pop("verify", False)
        ) as client:
            return client.put(**kwargs)

    def request(self, **kwargs) -> httpx.Response:
        headers = kwargs.pop("headers", {})
        self._update_headers(headers)
        with httpx.Client(
            headers=headers, cookies=kwargs.pop("cookies", None), verify=kwargs.pop("verify", False)
        ) as client:
            return client.request(**kwargs)

    async def aio_delete(self, **kwargs) -> httpx.Response:
        headers = kwargs.pop("headers", {})
        self._update_headers(headers)
        async with httpx.AsyncClient(
            headers=headers, cookies=kwargs.pop("cookies", None), verify=kwargs.pop("verify", False)
        ) as client:
            return await client.delete(**kwargs)

    async def aio_get(self, **kwargs) -> httpx.Response:
        headers = kwargs.pop("headers", {})
        self._update_headers(headers)
        async with httpx.AsyncClient(
            headers=headers, cookies=kwargs.pop("cookies", None), verify=kwargs.pop("verify", False)
        ) as client:
            return await client.get(**kwargs)

    async def aio_patch(self, **kwargs) -> httpx.Response:
        headers = kwargs.pop("headers", {})
        self._update_headers(headers)
        async with httpx.AsyncClient(
            headers=headers, cookies=kwargs.pop("cookies", None), verify=kwargs.pop("verify", False)
        ) as client:
            return await client.patch(**kwargs)

    async def aio_post(self, **kwargs) -> httpx.Response:
        headers = kwargs.pop("headers", {})
        self._update_headers(headers)
        async with httpx.AsyncClient(
            headers=headers, cookies=kwargs.pop("cookies", None), verify=kwargs.pop("verify", False)
        ) as client:
            return await client.post(**kwargs)

    async def aio_put(self, **kwargs) -> httpx.Response:
        headers = kwargs.pop("headers", {})
        self._update_headers(headers)
        async with httpx.AsyncClient(
            headers=headers, cookies=kwargs.pop("cookies", None), verify=kwargs.pop("verify", False)
        ) as client:
            return await client.put(**kwargs)

    async def aio_request(self, **kwargs) -> httpx.Response:
        headers = kwargs.pop("headers", {})
        self._update_headers(headers)
        async with httpx.AsyncClient(
            headers=headers, cookies=kwargs.pop("cookies", None), verify=kwargs.pop("verify", False)
        ) as client:
            return await client.request(**kwargs)


TPRequestorInstance = Annotated[TPRequestor, Depends(TPRequestor)]

__all__ = ["TPRequestor", "TPRequestorInstance"]
