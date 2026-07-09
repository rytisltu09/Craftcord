from __future__ import annotations

from typing import Any

from craftcord.minecraft.client import MinecraftClient


class StubRequester:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any] | None]] = []

    async def request(self, action: str, payload: dict[str, Any] | None = None) -> Any:
        self.calls.append((action, payload))
        responses = {
            "minecraft.get_players": {
                "players": [
                    {
                        "uuid": "player-1",
                        "username": "Alex",
                        "health": 20,
                        "world": "world",
                        "location": {"x": 1, "y": 64, "z": 2},
                    }
                ]
            },
            "minecraft.get_server_info": {
                "version": "1.21",
                "online_players": 3,
                "max_players": 20,
                "uptime": 512.5,
            },
            "minecraft.execute": {"success": True},
            "minecraft.send_message": {},
            "minecraft.kick": {},
        }
        return responses[action]


async def test_minecraft_client_models() -> None:
    requester = StubRequester()
    client = MinecraftClient(requester)

    players = await client.get_players()
    info = await client.get_server_info()

    assert players[0].username == "Alex"
    assert players[0].location.y == 64.0
    assert info.version == "1.21"
    assert info.online_players == 3


async def test_minecraft_client_actions() -> None:
    requester = StubRequester()
    client = MinecraftClient(requester)

    await client.send_message("Hello")
    await client.execute("say Hello")
    await client.kick("Alex", reason="Testing")

    assert requester.calls == [
        ("minecraft.send_message", {"message": "Hello"}),
        ("minecraft.execute", {"command": "say Hello"}),
        ("minecraft.kick", {"username": "Alex", "reason": "Testing"}),
    ]
