from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from craftcord.core.events import BaseEvent
from craftcord.core.exceptions import DiscordAdapterError
from craftcord.discord.adapter import DiscordAdapter


class DiscordPyAdapter(DiscordAdapter):
    def __init__(
        self,
        bot: Any,
        *,
        default_channel: int | str | None = None,
        command_responder: Callable[[str, Any], Awaitable[None]] | None = None,
        event_forwarder: Callable[[BaseEvent], Awaitable[None]] | None = None,
    ) -> None:
        super().__init__()
        self._bot = bot
        self._default_channel = default_channel
        self._command_responder = command_responder
        self._event_forwarder = event_forwarder

    async def send(self, message: str, /, *, channel: str | int | None = None) -> Any:
        channel_id = channel if channel is not None else self._default_channel
        if channel_id is None:
            raise DiscordAdapterError("No Discord channel was configured for DiscordPyAdapter")

        target = self._bot.get_channel(int(channel_id))
        if target is None:
            raise DiscordAdapterError(f"Discord channel {channel_id!r} was not found")
        return await target.send(message)

    async def respond(self, command_name: str, result: Any) -> None:
        if self._command_responder is None:
            await super().respond(command_name, result)
            return

        await self._command_responder(command_name, result)

    async def forward_event(self, event: BaseEvent) -> None:
        if self._event_forwarder is None:
            await super().forward_event(event)
            return

        await self._event_forwarder(event)
