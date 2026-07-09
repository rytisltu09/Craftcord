from __future__ import annotations

import asyncio
import contextlib
import json
from typing import Any
from uuid import uuid4

from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosed

from craftcord.core.config import ClientConfig
from craftcord.core.exceptions import (
    AuthenticationError,
    ConnectionClosedError,
    ProtocolError,
    RequestTimeoutError,
)
from craftcord.transport.base import Transport


class WebSocketTransport(Transport):
    def __init__(self, config: ClientConfig) -> None:
        super().__init__(config)
        self._websocket: ClientConnection | None = None
        self._pending: dict[str, asyncio.Future[Any]] = {}
        self._connected = asyncio.Event()
        self._connection_lock = asyncio.Lock()
        self._send_lock = asyncio.Lock()
        self._receiver_task: asyncio.Task[None] | None = None
        self._heartbeat_task: asyncio.Task[None] | None = None
        self._running = False
        self._closing = False

    @property
    def is_connected(self) -> bool:
        return self._connected.is_set() and self._websocket is not None

    async def connect(self) -> None:
        if self.is_connected:
            return

        async with self._connection_lock:
            if self.is_connected:
                return

            self._running = True
            self._closing = False
            await self._connect_with_retries()

            if self._heartbeat_task is None or self._heartbeat_task.done():
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def close(self) -> None:
        self._running = False
        self._closing = True
        self._connected.clear()

        await self._fail_pending(ConnectionClosedError("Transport closed"))
        await self._cancel_task(self._heartbeat_task)
        await self._cancel_task(self._receiver_task)

        if self._websocket is not None:
            await self._websocket.close()
            self._websocket = None

    async def request(self, action: str, payload: dict[str, Any] | None = None) -> Any:
        if self._websocket is None:
            await self.connect()

        try:
            await asyncio.wait_for(self._connected.wait(), timeout=self.config.connect_timeout)
        except TimeoutError as exc:
            raise ConnectionClosedError("Timed out waiting for WebSocket connection") from exc

        request_id = str(uuid4())
        loop = asyncio.get_running_loop()
        future: asyncio.Future[Any] = loop.create_future()
        self._pending[request_id] = future
        message = {
            "type": "request",
            "id": request_id,
            "action": action,
            "payload": payload or {},
        }

        try:
            async with self._send_lock:
                websocket = self._require_socket()
                await websocket.send(json.dumps(message))
            return await asyncio.wait_for(future, timeout=self.config.request_timeout)
        except TimeoutError as exc:
            raise RequestTimeoutError(f"Timed out waiting for response to '{action}'") from exc
        finally:
            self._pending.pop(request_id, None)

    async def _connect_with_retries(self) -> None:
        backoff = self.config.reconnect_backoff

        while self._running and not self._closing:
            try:
                await self._connect_once()
                return
            except AuthenticationError:
                raise
            except Exception as exc:
                if not self.config.reconnect:
                    raise ConnectionClosedError("WebSocket connection failed") from exc
                self._logger.warning("WebSocket connection failed, retrying in %.2fs", backoff)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, self.config.reconnect_max_backoff)

        raise ConnectionClosedError(
            "WebSocket transport stopped before a connection was established"
        )

    async def _connect_once(self) -> None:
        headers = {
            "Authorization": f"Bearer {self.config.token}",
            "User-Agent": self.config.user_agent,
            **self.config.headers,
        }
        websocket = await connect(
            self.config.ws_url,
            open_timeout=self.config.connect_timeout,
            additional_headers=headers,
            ping_interval=None,
            close_timeout=self.config.connect_timeout,
        )
        self._websocket = websocket
        self._connected.set()

        if self._receiver_task is None or self._receiver_task.done():
            self._receiver_task = asyncio.create_task(self._receiver_loop())

        try:
            await self.request("auth.validate", {"token": self.config.token})
        except Exception:
            self._connected.clear()
            await websocket.close()
            self._websocket = None
            raise

    async def _receiver_loop(self) -> None:
        while self._running and not self._closing:
            websocket = self._websocket
            if websocket is None:
                return

            try:
                async for message in websocket:
                    await self._handle_message(message)
            except ConnectionClosed:
                pass
            finally:
                self._connected.clear()

            if self._closing or not self._running:
                return

            await self._fail_pending(ConnectionClosedError("WebSocket disconnected"))
            self._websocket = None
            await self._connect_with_retries()

    async def _handle_message(self, message: str) -> None:
        try:
            payload = json.loads(message)
        except json.JSONDecodeError as exc:
            raise ProtocolError("Received invalid JSON from WebSocket transport") from exc

        message_type = payload.get("type")
        if message_type == "response":
            request_id = str(payload.get("id", ""))
            future = self._pending.get(request_id)
            if future is None or future.done():
                return

            if payload.get("status", "ok") == "ok":
                future.set_result(payload.get("data", {}))
            else:
                future.set_exception(self._protocol_error_from_payload(payload))
            return

        if message_type == "event":
            event_name = str(payload.get("event", "unknown"))
            event_payload = dict(payload.get("data") or {})
            await self.emit_event(event_name, event_payload)
            return

        if message_type == "pong":
            return

        raise ProtocolError(f"Unsupported WebSocket message type: {message_type!r}")

    def _protocol_error_from_payload(self, payload: dict[str, Any]) -> Exception:
        code = str(payload.get("code", ""))
        error = str(payload.get("error", "Unknown transport error"))
        if code == "auth_failed":
            return AuthenticationError(error)
        return ProtocolError(error)

    def _require_socket(self) -> ClientConnection:
        if self._websocket is None:
            raise ConnectionClosedError("WebSocket is not connected")
        return self._websocket

    async def _heartbeat_loop(self) -> None:
        while self._running and not self._closing:
            await asyncio.sleep(self.config.heartbeat_interval)
            if not self.is_connected:
                continue

            try:
                waiter = await self._require_socket().ping()
                await asyncio.wait_for(waiter, timeout=self.config.request_timeout)
            except Exception:
                if self._websocket is not None:
                    await self._websocket.close()

    async def _fail_pending(self, exc: Exception) -> None:
        for future in list(self._pending.values()):
            if not future.done():
                future.set_exception(exc)
        self._pending.clear()

    async def _cancel_task(self, task: asyncio.Task[None] | None) -> None:
        if task is None:
            return
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
