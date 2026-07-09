from __future__ import annotations

from typing import Any

import pytest
from aiohttp import web

from craftcord.core.config import ClientConfig
from craftcord.core.exceptions import AuthenticationError
from craftcord.transport.http import HTTPTransport


@pytest.fixture
async def http_server(unused_tcp_port: int) -> Any:
    async def validate(request: web.Request) -> web.Response:
        if request.headers.get("Authorization") != "Bearer secret":
            return web.json_response({"status": "error", "error": "bad token"}, status=401)
        return web.json_response({"status": "ok"})

    async def rpc(request: web.Request) -> web.Response:
        if request.headers.get("Authorization") != "Bearer secret":
            return web.json_response({"status": "error", "error": "bad token"}, status=401)

        payload = await request.json()
        return web.json_response(
            {
                "status": "ok",
                "data": {
                    "action": payload["action"],
                    "payload": payload["payload"],
                },
            }
        )

    app = web.Application()
    app.router.add_get("/api/v1/auth/validate", validate)
    app.router.add_post("/api/v1/rpc", rpc)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", unused_tcp_port)
    await site.start()
    try:
        yield unused_tcp_port
    finally:
        await runner.cleanup()


async def test_http_transport_request(http_server: int) -> None:
    transport = HTTPTransport(
        ClientConfig(host="127.0.0.1", port=http_server, token="secret")
    )

    response = await transport.request("minecraft.execute", {"command": "say hi"})

    assert response == {
        "action": "minecraft.execute",
        "payload": {"command": "say hi"},
    }

    await transport.close()


async def test_http_transport_authentication_failure(http_server: int) -> None:
    transport = HTTPTransport(
        ClientConfig(host="127.0.0.1", port=http_server, token="wrong")
    )

    with pytest.raises(AuthenticationError):
        await transport.connect()

    await transport.close()
