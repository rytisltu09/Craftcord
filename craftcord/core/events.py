from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class BaseEvent:
    name: str
    raw: dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC), kw_only=True)


@dataclass(slots=True)
class GenericEvent(BaseEvent):
    data: dict[str, Any] = field(default_factory=dict)


def build_event(name: str, payload: dict[str, Any]) -> BaseEvent:
    from craftcord.minecraft.events import (
        PlayerChatEvent,
        PlayerDeathEvent,
        PlayerJoinEvent,
        PlayerLeaveEvent,
        ServerStartEvent,
        ServerStopEvent,
    )
    from craftcord.minecraft.models import Player

    if name == "player_join":
        return PlayerJoinEvent(name=name, raw=payload, player=Player.from_dict(payload["player"]))
    if name == "player_leave":
        return PlayerLeaveEvent(name=name, raw=payload, player=Player.from_dict(payload["player"]))
    if name == "player_chat":
        return PlayerChatEvent(
            name=name,
            raw=payload,
            player=Player.from_dict(payload["player"]),
            message=str(payload.get("message") or payload.get("content") or ""),
        )
    if name == "player_death":
        return PlayerDeathEvent(
            name=name,
            raw=payload,
            player=Player.from_dict(payload["player"]),
            reason=str(payload.get("reason") or payload.get("message") or "unknown"),
        )
    if name == "server_start":
        return ServerStartEvent(
            name=name,
            raw=payload,
            version=str(payload.get("version") or "unknown"),
        )
    if name == "server_stop":
        return ServerStopEvent(
            name=name,
            raw=payload,
            reason=str(payload.get("reason") or "shutdown"),
        )
    return GenericEvent(name=name, raw=payload, data=payload)
