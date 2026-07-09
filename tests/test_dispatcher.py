from __future__ import annotations

from craftcord.core.dispatcher import EventDispatcher


async def test_dispatcher_supports_multiple_listeners() -> None:
    dispatcher = EventDispatcher()
    received: list[str] = []

    @dispatcher.listener("player_join")
    async def first(event: str) -> None:
        received.append(f"first:{event}")

    @dispatcher.listener("player_join")
    async def second(event: str) -> None:
        received.append(f"second:{event}")

    await dispatcher.dispatch("player_join", "Alex")

    assert received == ["first:Alex", "second:Alex"]


async def test_dispatcher_can_unregister_listener() -> None:
    dispatcher = EventDispatcher()
    received: list[str] = []

    async def listener(event: str) -> None:
        received.append(event)

    dispatcher.add_listener("player_leave", listener)

    assert dispatcher.remove_listener("player_leave", listener) is True
    await dispatcher.dispatch("player_leave", "Alex")

    assert received == []
