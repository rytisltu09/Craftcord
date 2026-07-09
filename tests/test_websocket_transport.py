from __future__ import annotations

import asyncio
import json
from typing import Any

import pytest
from websockets.asyncio.server import ServerConnection, serve

from craftcord.core.config import ClientConfig
from craftcord.core.exceptions import AuthenticationError
from craftcord.transport.websocket import WebSocketTransport


@pytest.fixture
async def websocket_server(unused_tcp_port: int) -> Any:
    events: list[dict[str, Any]] = []

    async def handler(connection: ServerConnection) -> None:
        async for raw_message in connection:
            message = json.loads(raw_message)
            action = message.get("action")

            if action == "auth.validate":
                token = message.get("payload", {}).get("token")
                if token != "secret":
                    await connection.send(
                        json.dumps(
                            {
                                "type": "response",
                                "id": message["id"],
                                "status": "error",
                                "code": "auth_failed",
                                "error": "bad token",
                            }
                        )
                    )
                    continue

                await connection.send(
                    json.dumps(
                        {
                            "type": "response",
                            "id": message["id"],
                            "status": "ok",
                            "data": {"authenticated": True},
                        }
                    )
                )
                await connection.send(
                    json.dumps(
                        {
                            "type": "event",
                            "event": "player_join",
                            "data": {
                                "player": {
                                    "uuid": "player-1",
                                    "username": "Alex",
                                    "health": 20,
                                    "world": "world",
                                    "location": {"x": 0, "y": 64, "z": 0},
                                }
                            },
                        }
                    )
                )
                continue

            events.append(message)
            await connection.send(
                json.dumps(
                    {
                        "type": "response",
                        "id": message["id"],
                        "status": "ok",
                        "data": {"echo": message.get("payload", {})},
                    }
                )
            )

    server = await serve(handler, "127.0.0.1", unused_tcp_port)
    try:
        yield unused_tcp_port, events
    finally:
        server.close()
        await server.wait_closed()


async def test_websocket_transport_request_and_event(
    websocket_server: tuple[int, list[dict[str, Any]]],
) -> None:
    port, events = websocket_server
    transport = WebSocketTransport(ClientConfig(host="127.0.0.1", port=port, token="secret"))
    received: list[str] = []

    async def on_event(event_name: str, payload: dict[str, Any]) -> None:
        received.append(f"{event_name}:{payload['player']['username']}")

    transport.set_event_handler(on_event)
    response = await transport.request("minecraft.execute", {"command": "say hi"})

    assert response == {"echo": {"command": "say hi"}}

    await asyncio.sleep(0)

    assert received == ["player_join:Alex"]
    assert events == [
        {
            "type": "request",
            "id": events[0]["id"],
            "action": "minecraft.execute",
            "payload": {"command": "say hi"},
        }
    ]

    await transport.close()


async def test_websocket_transport_authentication_failure(
    websocket_server: tuple[int, list[dict[str, Any]]]
) -> None:
    port, _ = websocket_server
    transport = WebSocketTransport(ClientConfig(host="127.0.0.1", port=port, token="wrong"))

    with pytest.raises(AuthenticationError):
        await transport.connect()

    await transport.close()


async def test_websocket_transport_reconnect(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = WebSocketTransport(ClientConfig(host="127.0.0.1", port=12345, token="secret"))
    attempts = 0

    async def fake_connect_once() -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise OSError("connection refused")
        transport._connected.set()

    async def fake_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(transport, "_connect_once", fake_connect_once)
    monkeypatch.setattr("craftcord.transport.websocket.asyncio.sleep", fake_sleep)

    transport._running = True
    await transport._connect_with_retries()

    assert attempts == 2
