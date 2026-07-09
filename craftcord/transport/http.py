from __future__ import annotations

from typing import Any

import aiohttp

from craftcord.core.config import ClientConfig
from craftcord.core.exceptions import AuthenticationError, ProtocolError
from craftcord.transport.base import Transport


class HTTPTransport(Transport):
    def __init__(self, config: ClientConfig) -> None:
        super().__init__(config)
        self._session: aiohttp.ClientSession | None = None

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.token}",
            "User-Agent": self.config.user_agent,
            **self.config.headers,
        }

    async def connect(self) -> None:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)
            self._session = aiohttp.ClientSession(timeout=timeout, headers=self._headers)
        await self._validate_connection()

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

    async def request(self, action: str, payload: dict[str, Any] | None = None) -> Any:
        await self.connect()
        assert self._session is not None

        async with self._session.post(
            f"{self.config.http_url}/rpc",
            json={"action": action, "payload": payload or {}},
        ) as response:
            if response.status == 401:
                raise AuthenticationError("HTTP authentication failed")
            if response.status >= 400:
                raise ProtocolError(f"HTTP request failed with status {response.status}")
            data = await response.json()

        status = data.get("status", "ok")
        if status != "ok":
            error = data.get("error", "Unknown HTTP transport error")
            if data.get("code") == "auth_failed":
                raise AuthenticationError(str(error))
            raise ProtocolError(str(error))
        return data.get("data", {})

    async def _validate_connection(self) -> None:
        assert self._session is not None
        async with self._session.get(f"{self.config.http_url}/auth/validate") as response:
            if response.status == 401:
                raise AuthenticationError("HTTP authentication failed")
            if response.status >= 400:
                raise ProtocolError(f"HTTP validation failed with status {response.status}")
