# API Reference

## Client

`Client` coordinates connection lifecycle, event dispatching, Minecraft operations, and Discord adapters.

### Registration

```python
@client.on("player_chat")
async def handle_chat(event) -> None:
    print(event.message)

@client.command("online")
async def online_command() -> list[str]:
    players = await client.minecraft.players()
    return [player.username for player in players]
```

### Lifecycle

- `await client.connect()` connects without blocking the rest of your application
- `await client.start()` connects and waits until the client is closed
- `await client.close()` shuts down transports, adapters, and extensions cleanly

## MinecraftClient

- `await minecraft.send_message(message, target=None)`
- `await minecraft.execute(command)`
- `await minecraft.get_players()`
- `await minecraft.players()`
- `await minecraft.get_server_info()`
- `await minecraft.server_info()`
- `await minecraft.kick(username, reason=None)`

## Events

Built-in event types include:

- `player_join`
- `player_leave`
- `player_chat`
- `player_death`
- `server_start`
- `server_stop`

Each event arrives as a typed object when CraftCord knows the schema, or as `GenericEvent` for unknown event names.

## Transports

- `WebSocketTransport` is the primary transport and supports events, reconnects, heartbeats, and request-response messaging
- `HTTPTransport` supports authenticated RPC-style requests against a REST endpoint

## Discord Adapters

`DiscordAdapter` is the contract. `DiscordPyAdapter` integrates with `discord.py` by sending messages to configured channels and optionally forwarding results or events to your bot runtime.
