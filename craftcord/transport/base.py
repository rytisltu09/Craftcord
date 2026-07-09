from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any

from craftcord.core.config import ClientConfig
from craftcord.utils.logging import get_logger

EventHandler = Callable[[str, dict[str, Any]], Awaitable[None]]


class Transport(ABC):
    def __init__(self, config: ClientConfig) -> None:
        self.config = config
        self._event_handler: EventHandler | None = None
        self._logger = get_logger(f"craftcord.transport.{self.__class__.__name__.lower()}")

    def set_event_handler(self, handler: EventHandler) -> None:
        self._event_handler = handler

    async def emit_event(self, event_name: str, payload: dict[str, Any]) -> None:
        if self._event_handler is not None:
            await self._event_handler(event_name, payload)

    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def request(self, action: str, payload: dict[str, Any] | None = None) -> Any: ...
