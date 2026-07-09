from __future__ import annotations

from typing import Any, Protocol

from craftcord.minecraft.models import Player, ServerInfo


class Requester(Protocol):
    async def request(self, action: str, payload: dict[str, Any] | None = None) -> Any: ...


class MinecraftClient:
    def __init__(self, requester: Requester) -> None:
        self._requester = requester

    async def send_message(self, message: str, *, target: str | None = None) -> None:
        payload: dict[str, Any] = {"message": message}
        if target is not None:
            payload["target"] = target
        await self._requester.request("minecraft.send_message", payload)

    async def execute(self, command: str) -> dict[str, Any]:
        response = await self._requester.request("minecraft.execute", {"command": command})
        return dict(response or {})

    async def get_players(self) -> list[Player]:
        response = await self._requester.request("minecraft.get_players")
        players = response.get("players", response)
        return [Player.from_dict(player) for player in players]

    async def players(self) -> list[Player]:
        return await self.get_players()

    async def get_server_info(self) -> ServerInfo:
        response = await self._requester.request("minecraft.get_server_info")
        data = response.get("server", response)
        return ServerInfo.from_dict(data)

    async def server_info(self) -> ServerInfo:
        return await self.get_server_info()

    async def kick(self, username: str, *, reason: str | None = None) -> None:
        payload: dict[str, Any] = {"username": username}
        if reason is not None:
            payload["reason"] = reason
        await self._requester.request("minecraft.kick", payload)
    
    async def ban(self, username: str, *, reason: str | None = None) -> None:
        payload: dict[str, Any] = {"username": username}
        if reason is not None:
            payload["reason"] = reason
        await self._requester.request("minecraft.ban", payload)
