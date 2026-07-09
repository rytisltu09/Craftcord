from __future__ import annotations

from dataclasses import dataclass

from craftcord.core.events import BaseEvent
from craftcord.minecraft.models import Player


@dataclass(slots=True)
class PlayerJoinEvent(BaseEvent):
    player: Player


@dataclass(slots=True)
class PlayerLeaveEvent(BaseEvent):
    player: Player


@dataclass(slots=True)
class PlayerChatEvent(BaseEvent):
    player: Player
    message: str


@dataclass(slots=True)
class PlayerDeathEvent(BaseEvent):
    player: Player
    reason: str


@dataclass(slots=True)
class ServerStartEvent(BaseEvent):
    version: str


@dataclass(slots=True)
class ServerStopEvent(BaseEvent):
    reason: str
