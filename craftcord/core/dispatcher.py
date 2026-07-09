from __future__ import annotations

import asyncio
import inspect
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

Listener = Callable[[Any], Awaitable[Any] | Any]
T = TypeVar("T", bound=Listener)


class EventDispatcher:
    def __init__(self) -> None:
        self._listeners: dict[str, list[Listener]] = defaultdict(list)

    def add_listener(self, event_name: str, listener: Listener) -> None:
        self._listeners[event_name].append(listener)

    def remove_listener(self, event_name: str, listener: Listener) -> bool:
        listeners = self._listeners.get(event_name)
        if not listeners:
            return False

        try:
            listeners.remove(listener)
        except ValueError:
            return False

        if not listeners:
            self._listeners.pop(event_name, None)
        return True

    def listener(self, event_name: str) -> Callable[[T], T]:
        def decorator(listener: T) -> T:
            self.add_listener(event_name, listener)
            return listener

        return decorator

    async def dispatch(self, event_name: str, event: Any) -> list[Any]:
        listeners = [*self._listeners.get(event_name, []), *self._listeners.get("*", [])]
        results: list[Any] = []
        coroutines: list[Awaitable[Any]] = []

        for listener in listeners:
            outcome = listener(event)
            if inspect.isawaitable(outcome):
                coroutines.append(outcome)
            else:
                results.append(outcome)

        if coroutines:
            results.extend(await asyncio.gather(*coroutines))
        return results
