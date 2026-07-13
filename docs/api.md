# API Reference

## Client

`Client` coordinates connection lifecycle, event dispatching, and Minecraft operations.

### Connection Configuration

`Client` and `ClientConfig` use host/port targeting, where the target must be reachable from the SDK process.

Plugin network exposure is controlled on the Java side:

- `bindMode=local` binds plugin server to `127.0.0.1`
- `bindMode=global` binds plugin server to `0.0.0.0`
- non-empty `host` overrides `bindMode` and binds a specific interface

Use a reachable address in SDK config:

- same machine: `127.0.0.1`
- LAN: server LAN IP such as `192.168.1.50`
- public/proxy: proxy hostname such as `craftcord.example.com`

Do not set SDK host to `0.0.0.0`; CraftCord rejects this because wildcard bind addresses are not valid client destinations.

Examples:

- `http://127.0.0.1:8080/api/v1`
- `http://<server-lan-ip>:8080/api/v1`
- `https://craftcord.example.com/api/v1`

Endpoint paths are unchanged by this networking update.

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
- `await client.close()` shuts down transports and extensions cleanly

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

## Discord Integration

CraftCord no longer ships a built-in Discord adapter. Integrate events and commands directly in your own bot runtime (for example, with `discord.py`) by registering CraftCord event handlers and sending messages with your bot client.
