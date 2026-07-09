from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Location:
    x: float
    y: float
    z: float
    yaw: float | None = None
    pitch: float | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Location:
        return cls(
            x=float(data.get("x", 0.0)),
            y=float(data.get("y", 0.0)),
            z=float(data.get("z", 0.0)),
            yaw=float(data["yaw"]) if data.get("yaw") is not None else None,
            pitch=float(data["pitch"]) if data.get("pitch") is not None else None,
        )


@dataclass(slots=True)
class Player:
    uuid: str
    username: str
    health: float
    world: str
    location: Location

    @property
    def name(self) -> str:
        return self.username

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Player:
        return cls(
            uuid=str(data.get("uuid", "")),
            username=str(data.get("username") or data.get("name") or ""),
            health=float(data.get("health", 20.0)),
            world=str(data.get("world", "world")),
            location=Location.from_dict(dict(data.get("location") or {})),
        )


@dataclass(slots=True)
class ServerInfo:
    version: str
    online_players: int
    max_players: int
    uptime: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ServerInfo:
        return cls(
            version=str(data.get("version", "unknown")),
            online_players=int(data.get("online_players", 0)),
            max_players=int(data.get("max_players", 0)),
            uptime=float(data.get("uptime", 0.0)),
        )
