# CraftCord

CraftCord is a Python SDK for Discord bot developers who want to connect their bot to Minecraft.

If you are new, the fastest way to understand CraftCord is:

1. Run the example bot.
2. Use `!mc_online` in Discord.
3. See Minecraft player data in your Discord channel.

## Who This Is For

CraftCord is a good fit if you want to:

- build a Discord bot in Python
- read Minecraft server events
- run Minecraft actions from Discord commands
- keep bot logic clean and reusable

## What You Get

- async Python client (`Client`)
- two transport options: WebSocket or HTTP
- typed Minecraft events and models
- CraftCord command system (`@client.command`)
- Discord adapter for `discord.py` (`DiscordPyAdapter`)
- plugin system (`client.plugins.load(...)`)

## Beginner 5-Minute Setup

### 1. Install Dependencies

From your project root:

```bash
python -m pip install -e ".[dev,discord]"
```

If you only need runtime dependencies:

```bash
python -m pip install "craftcord[discord]"
```

### 2. Configure Environment Variables

Set these before running `examples/basic_bot.py`:

- `DISCORD_TOKEN` (required)
- `CRAFTCORD_HOST` (default: `127.0.0.1`)
- `CRAFTCORD_PORT` (default: `8080`)
- `CRAFTCORD_TOKEN` (default: `secret`)
- `CRAFTCORD_TRANSPORT` (`ws` or `http`, default: `ws`)
- `CRAFTCORD_DEFAULT_CHANNEL` (optional Discord channel id)

Example:

```bash
export DISCORD_TOKEN="your-discord-bot-token"
export CRAFTCORD_HOST="127.0.0.1"
export CRAFTCORD_PORT="8080"
export CRAFTCORD_TOKEN="secret"
export CRAFTCORD_TRANSPORT="ws"
```

### Local vs Global Plugin Exposure

The Java CraftCord plugin now controls network exposure with:

- `bindMode=local` -> plugin binds to `127.0.0.1` (same machine only)
- `bindMode=global` -> plugin binds to `0.0.0.0` (all interfaces)
- `host=<non-empty-ip-or-hostname>` -> overrides `bindMode` and binds that specific interface

SDK connection guidance:

- Client targets must be reachable from where your Python app runs.
- Do not use `0.0.0.0` as a client target address. It is a server bind wildcard, not a routable destination.
- API endpoints and paths are unchanged (`/api/v1/*`, `/ws`).

Use these connection URLs as a reference:

- Local same-machine: `http://127.0.0.1:8080/api/v1`
- LAN client: `http://<server-lan-ip>:8080/api/v1`
- Reverse proxy/public endpoint: `https://craftcord.example.com/api/v1`

Plugin startup logs now include binding type (`local-only`, `global-all-interfaces`, or `specific-interface`) so you can confirm exposure mode quickly.

### 3. Start The Bot

```bash
python examples/basic_bot.py
```

### 4. Test It In Discord

In a channel where your bot can read and send messages, run:

```text
!mc_online
```

If everything is connected, the bot responds with online player names.

## How Commands Work (Simple Mental Model)

- `@bot.command` is Discord-facing.
- `@client.command` is CraftCord-facing shared logic.

Typical flow:

1. User types a Discord command like `!mc_online`.
2. Discord handler calls `await client.invoke_command("online")`.
3. CraftCord command runs and returns data.
4. Discord handler sends the result back to chat.

This is why you avoid duplicating business logic.

## Minimal Example

```python
import asyncio

from craftcord import Client


async def main() -> None:
    client = Client(host="127.0.0.1", port=8080, token="secret")

    @client.command("online")
    async def online_players() -> list[str]:
        players = await client.minecraft.players()
        return [player.username for player in players]

    await client.start()


asyncio.run(main())
```

## Minecraft Features Available

From `client.minecraft`:

- `players()` / `get_players()`
- `server_info()` / `get_server_info()`
- `send_message(message, target=None)`
- `execute(command)`
- `kick(username, reason=None)`
- `ban(username, reason=None)`

## Events You Can Listen To

Typed built-in events include:

- `player_join`
- `player_leave`
- `player_chat`
- `player_death`
- `server_start`
- `server_stop`

Unknown event names arrive as `GenericEvent`.

## Transport Choice

- Use `ws` for real-time events and long-running bot sessions.
- Use `http` for simple request/response integrations.

Set with:

```bash
export CRAFTCORD_TRANSPORT="ws"
```

or

```bash
export CRAFTCORD_TRANSPORT="http"
```

## Troubleshooting

### Connection refused or timeout

Check this order:

1. Verify Java plugin `bindMode` and optional `host` values.
2. Confirm your SDK `CRAFTCORD_HOST` points to a reachable address from the client machine.
3. Never set SDK `CRAFTCORD_HOST` to `0.0.0.0`.
4. Verify `CRAFTCORD_PORT` and `CRAFTCORD_TOKEN` match plugin config.
5. Ensure host firewall rules allow inbound traffic on the plugin port.
6. For LAN/WAN access, verify NAT/port-forwarding and routing.
7. If using a reverse proxy, ensure `/api/v1/*` and `/ws` route to the plugin upstream.

### Bot starts but keeps retrying WebSocket

Cause: CraftCord API endpoint is not reachable.

Check:

1. Is your Java-side CraftCord plugin/API running?
2. Do `CRAFTCORD_HOST`, `CRAFTCORD_PORT`, and `CRAFTCORD_TOKEN` match?
3. If your server only supports HTTP, set `CRAFTCORD_TRANSPORT=http`.

### Discord command does not trigger

Check:

1. Message Content Intent is enabled in Discord Developer Portal.
2. Bot has permission to read and send in that channel.
3. You are using the right prefix (`!`) and command (`!mc_online`).

### Import or dataclass errors on Python 3.14

Use the latest code in this repository. Recent updates include Python 3.14 compatibility fixes for event dataclasses.

## Plugin System

Extensions are classes with `setup(client)` and optional `teardown(client)`.

```python
class GreetingExtension:
    async def setup(self, client) -> None:
        @client.on("player_join")
        async def greet(event) -> None:
            await client.minecraft.send_message(f"Welcome {event.player.username}!")


await client.plugins.load(GreetingExtension())
```

## Protocol Contract (For Java Plugin Authors)

## Migration Note (Plugin Networking Update)

- New plugin exposure options: `bindMode` (`local|global`) and optional `host` override.
- SDK API contract is unchanged: endpoints remain `/api/v1/auth/validate`, `/api/v1/rpc`, and `/ws`.
- Existing users with explicit SDK host/port configuration continue to work unchanged.
- SDK now rejects `0.0.0.0` as a client target host with a clear validation error.

Expected API behavior:

- Bearer token auth for HTTP and WebSocket
- WebSocket action: `auth.validate`
- HTTP endpoint: `GET /api/v1/auth/validate`
- HTTP endpoint: `POST /api/v1/rpc`
- WebSocket event envelope support

Request envelope:

```json
{
  "type": "request",
  "id": "uuid",
  "action": "minecraft.get_players",
  "payload": {}
}
```

Response envelope:

```json
{
  "type": "response",
  "id": "uuid",
  "status": "ok",
  "data": {}
}
```

Event envelope:

```json
{
  "type": "event",
  "event": "player_join",
  "data": {
    "player": {
      "uuid": "3b5e4f2d-8e34-4ad1-848f-b9d66fd07a4f",
      "username": "Alex",
      "health": 20.0,
      "world": "world",
      "location": {"x": 0.0, "y": 64.0, "z": 0.0}
    }
  }
}
```

## Development

Run tests:

```bash
pytest
```

Run lint:

```bash
ruff check .
```

## Repository Layout

```text
craftcord/
docs/
examples/
tests/
```
