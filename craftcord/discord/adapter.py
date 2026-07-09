from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from craftcord.core.events import BaseEvent
from craftcord.utils.logging import get_logger

if TYPE_CHECKING:
    from craftcord.client import Client


class DiscordAdapter(ABC):
    def __init__(self) -> None:
        self._client: Client | None = None
        self._logger = get_logger(f"craftcord.discord.{self.__class__.__name__.lower()}")

    def bind(self, client: Client) -> None:
        self._client = client

    async def startup(self) -> None:
        return None

    async def shutdown(self) -> None:
        return None

    @abstractmethod
    async def send(self, message: str, /, *, channel: str | int | None = None) -> Any: ...

    async def respond(self, command_name: str, result: Any) -> None:
        self._logger.debug("No Discord command responder configured for %s", command_name)

    async def forward_event(self, event: BaseEvent) -> None:
        self._logger.debug("Ignoring forwarded event %s", event.name)


class NullDiscordAdapter(DiscordAdapter):
    async def send(self, message: str, /, *, channel: str | int | None = None) -> None:
        destination = f" channel={channel}" if channel is not None else ""
        self._logger.info(
            "Discord adapter not configured; dropping message:%s %s",
            destination,
            message,
        )
