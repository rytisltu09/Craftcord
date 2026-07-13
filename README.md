# CraftCord

CraftCord is an async Python SDK for talking to Minecraft Paper servers through CraftCordPlugin.

It provides a clean API for requests and live events over HTTP or WebSocket, so your app can focus on behavior instead of protocol plumbing.

Note:

- CraftCord requires CraftCordPlugin on your Paper server.
- Plugin repository: https://github.com/rytisltu09/CraftcordPlugin

## What Changed

CraftCord no longer ships a built-in Discord adapter layer.

Use CraftCord as your Minecraft transport/event SDK, and wire Discord behavior directly in your own bot runtime (for example, discord.py).

This keeps the SDK simpler and avoids framework-specific abstractions.

## Features

- Async-first API
- HTTP and WebSocket transports
- Typed Minecraft models
- Event dispatcher with typed events + GenericEvent fallback
- Built-in command registry/invocation
- Python-side plugin manager
- Framework-agnostic integration pattern for Discord bots and other Python apps

## Installation

```bash
pip install craftcord
```

If your application uses discord.py, install it in your app environment:

```bash
pip install discord.py
```

## Quick Start

### Environment Variables

```bash
export CRAFTCORD_HOST="127.0.0.1"
export CRAFTCORD_PORT="8080"
export CRAFTCORD_TOKEN="your-api-token"
export CRAFTCORD_TRANSPORT="ws"
```

### Minimal Client

```python
import asyncio

from craftcord import Client


async def main() -> None:
    client = Client(host="127.0.0.1", port=8080, token="secret")

    @client.command("online")
    async def online() -> list[str]:
        players = await client.minecraft.players()
        return [p.username for p in players]

    await client.start()


asyncio.run(main())
```

## Discord Integration (Direct)

CraftCord emits typed events you can handle directly and forward to Discord with your own bot.

Example: send a Discord embed when Minecraft emits server_start.

```python
import discord
from discord.ext import commands

from craftcord import Client
from craftcord.minecraft.events import ServerStartEvent

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
craft = Client(host="127.0.0.1", port=8080, token="secret")
DEFAULT_CHANNEL_ID = 123456789012345678


@craft.event("server_start")
async def on_server_start(event: ServerStartEvent) -> None:
    channel = bot.get_channel(DEFAULT_CHANNEL_ID)
    if channel is None:
        return

    embed = discord.Embed(
        title="Minecraft Server Started",
        description="The server is now online.",
        color=discord.Color.green(),
        timestamp=event.timestamp,
    )
    embed.add_field(name="Version", value=event.version, inline=True)
    await channel.send(embed=embed)
```

For a full working example, see examples/basic_bot.py.

## Core API

Common Minecraft operations:

```python
await client.minecraft.players()
await client.minecraft.server_info()
await client.minecraft.send_message("Hello from CraftCord")
await client.minecraft.execute("time set day")
await client.minecraft.kick("Steve", reason="Rule violation")
await client.minecraft.ban("Steve", reason="Griefing")
```

Register event handlers:

```python
@client.on("player_join")
async def on_join(event) -> None:
    print(event.player.username)
```

Built-in typed event names:

- player_join
- player_leave
- player_chat
- player_death
- server_start
- server_stop

Unknown events are delivered as GenericEvent.

## Transport Choice

WebSocket transport (default):

- Best for bots, dashboards, and real-time event streams.

```bash
export CRAFTCORD_TRANSPORT="ws"
```

HTTP transport:

- Best for scripts and one-off request/response workflows.

```bash
export CRAFTCORD_TRANSPORT="http"
```

## Network Binding and Reachability

CraftCordPlugin bind behavior is configured on the Java plugin side:

- bindMode=local binds to 127.0.0.1
- bindMode=global binds to 0.0.0.0
- host=<ip-or-hostname> overrides bindMode

Your Python SDK host must be a reachable destination from the SDK process.

Do not use 0.0.0.0 as CRAFTCORD_HOST.

Example targets:

- Same machine: http://127.0.0.1:8080/api/v1
- LAN client: http://<server-lan-ip>:8080/api/v1
- Public/proxy: https://craftcord.example.com/api/v1

## Troubleshooting

Connection refused or timeout checklist:

1. Ensure CraftCordPlugin is running.
2. Confirm token and port match plugin config.
3. Confirm CRAFTCORD_HOST points to a reachable address.
4. Do not use 0.0.0.0 as client host.
5. Check firewalls, routing, and reverse proxy forwarding.

WebSocket reconnect loop checklist:

1. Verify host, port, and token.
2. Verify plugin is reachable from the client machine.
3. If you only need request/response, switch to HTTP transport.

discord.py integration checklist:

1. Enable Message Content Intent when needed.
2. Ensure bot permissions include reading and sending messages.
3. Verify channel ID and command prefix.

## Plugin System

Load reusable Python plugins (extensions):

```python
class GreetingPlugin:
    async def setup(self, client) -> None:
        @client.on("player_join")
        async def greet(event) -> None:
            await client.minecraft.send_message(f"Welcome {event.player.username}!")


await client.plugins.load(GreetingPlugin)
```

## Protocol

CraftCord uses authenticated JSON-RPC style messages over HTTP and WebSocket.

Authentication model:

- Bearer token
- HTTP validation endpoint
- WebSocket authentication handshake

Endpoint paths:

- /api/v1/auth/validate
- /api/v1/rpc
- /ws

Sample request payload:

```json
{
  "type": "request",
  "id": "uuid",
  "action": "minecraft.get_players",
  "payload": {}
}
```

## Development

```bash
pytest
ruff check .
```

## Repository Structure

```text
craftcord/
├── craftcord/
├── docs/
├── examples/
└── tests/
```

## License

MIT
