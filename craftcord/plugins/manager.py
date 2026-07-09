from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Protocol

from craftcord.core.exceptions import PluginError

if TYPE_CHECKING:
    from craftcord.client import Client


class ExtensionProtocol(Protocol):
    async def setup(self, client: Client) -> None: ...

    async def teardown(self, client: Client) -> None: ...


class PluginManager:
    def __init__(self, client: Client) -> None:
        self._client = client
        self._extensions: dict[str, object] = {}

    async def load(self, extension: object) -> object:
        instance = extension() if inspect.isclass(extension) else extension
        setup = getattr(instance, "setup", None)
        if setup is None:
            raise PluginError("Extension must define an async setup(client) method")

        result = setup(self._client)
        await self._await_if_needed(result)
        self._extensions[instance.__class__.__name__] = instance
        return instance

    async def unload(self, name: str) -> bool:
        extension = self._extensions.pop(name, None)
        if extension is None:
            return False

        teardown = getattr(extension, "teardown", None)
        if teardown is not None:
            await self._await_if_needed(teardown(self._client))
        return True

    async def unload_all(self) -> None:
        for name in list(self._extensions):
            await self.unload(name)

    @property
    def loaded(self) -> dict[str, object]:
        return dict(self._extensions)

    async def _await_if_needed(self, result: object) -> None:
        if inspect.isawaitable(result):
            await result
