from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from craftcord.core.config import ClientConfig
from craftcord.core.dispatcher import EventDispatcher
from craftcord.core.events import BaseEvent, build_event
from craftcord.core.exceptions import CommandNotFoundError
from craftcord.discord.adapter import DiscordAdapter, NullDiscordAdapter
from craftcord.minecraft.client import MinecraftClient
from craftcord.plugins.manager import PluginManager
from craftcord.transport.base import Transport
from craftcord.transport.websocket import WebSocketTransport
from craftcord.utils.logging import get_logger

EventHandler = Callable[[BaseEvent], Awaitable[Any] | Any]
CommandHandler = Callable[..., Awaitable[Any] | Any]
TransportFactory = Callable[[ClientConfig], Transport]
T = TypeVar("T")


class Client:
    def __init__(
        self,
        *,
        host: str,
        port: int,
        token: str,
        transport: Transport | TransportFactory | None = None,
        discord_adapter: DiscordAdapter | None = None,
        config: ClientConfig | None = None,
    ) -> None:
        self.config = config or ClientConfig(host=host, port=port, token=token)
        self._logger = get_logger("craftcord.client")
        self._dispatcher = EventDispatcher()
        self._commands: dict[str, CommandHandler] = {}
        self._started = False
        self._closed = asyncio.Event()
        self._closed.set()

        self.transport = self._build_transport(transport)
        self.transport.set_event_handler(self._handle_transport_event)

        self.discord = discord_adapter or NullDiscordAdapter()
        self.discord.bind(self)

        self.minecraft = MinecraftClient(self)
        self.plugins = PluginManager(self)

    def _build_transport(self, transport: Transport | TransportFactory | None) -> Transport:
        if transport is None:
            return WebSocketTransport(self.config)
        if isinstance(transport, Transport):
            return transport
        return transport(self.config)

    async def __aenter__(self) -> Client:
        await self.connect()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    def on(self, event_name: str) -> Callable[[EventHandler], EventHandler]:
        def decorator(listener: EventHandler) -> EventHandler:
            self._dispatcher.add_listener(event_name, listener)
            return listener

        return decorator

    def event(self, event_name: str) -> Callable[[EventHandler], EventHandler]:
        return self.on(event_name)

    def remove_listener(self, event_name: str, listener: EventHandler) -> bool:
        return self._dispatcher.remove_listener(event_name, listener)

    def command(self, name: str | None = None) -> Callable[[CommandHandler], CommandHandler]:
        def decorator(handler: CommandHandler) -> CommandHandler:
            command_name = name or handler.__name__
            self._commands[command_name] = handler
            return handler

        return decorator

    async def connect(self) -> None:
        if self._started:
            return
        self._started = True
        self._closed.clear()
        await self.discord.startup()
        await self.transport.connect()

    async def start(self) -> None:
        await self.connect()
        await self.wait_closed()

    async def close(self) -> None:
        if not self._started:
            return
        self._started = False
        await self.transport.close()
        await self.plugins.unload_all()
        await self.discord.shutdown()
        self._closed.set()

    async def wait_closed(self) -> None:
        await self._closed.wait()

    async def request(self, action: str, payload: dict[str, Any] | None = None) -> Any:
        return await self.transport.request(action, payload or {})

    async def invoke_command(self, name: str, *args: Any, **kwargs: Any) -> Any:
        handler = self._commands.get(name)
        if handler is None:
            raise CommandNotFoundError(name)

        result = handler(*args, **kwargs)
        if inspect.isawaitable(result):
            return await result
        return result

    async def _handle_transport_event(self, event_name: str, payload: dict[str, Any]) -> None:
        if event_name == "command_request":
            command_name = str(payload.get("command", ""))
            result = await self.invoke_command(
                command_name,
                *(payload.get("args") or []),
                **(payload.get("kwargs") or {}),
            )
            await self.discord.respond(command_name, result)
            return

        event = build_event(event_name, payload)
        await self._dispatcher.dispatch(event_name, event)
        await self.discord.forward_event(event)
