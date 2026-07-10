# CraftCord

**CraftCord is an asynchronous Python SDK for communicating with Minecraft Paper servers through the CraftCordPlugin.**

It enables Python applications to interact with Minecraft using a simple, high-level API over HTTP or WebSockets.

Whether you're building a Discord bot, web dashboard, desktop application, mobile app, automation service, or another custom integration, CraftCord provides a clean and modern interface for interacting with your Minecraft server.

> **Note**
>
> CraftCord requires the **CraftCordPlugin** to be installed on your Paper server.
>
> Plugin Repository:
> https://github.com/rytisltu09/CraftcordPlugin

---

# Why CraftCord?

CraftCord removes the complexity of talking directly to a Minecraft server.

Instead of implementing HTTP requests, WebSocket connections, authentication, and event parsing yourself, CraftCord provides an intuitive Python API.

With only a few lines of code you can:

- Retrieve online players
- Execute Minecraft commands
- Send chat messages
- Listen for live server events
- Build integrations with any Python application

---

# Perfect For

CraftCord is suitable for:

- Discord bots
- Web dashboards
- Desktop applications
- Mobile applications
- Automation tools
- Monitoring systems
- Economy integrations
- Administrative panels
- Any custom Python application

---

# Features

- Asynchronous Python API
- HTTP and WebSocket transports
- Typed Minecraft models
- Event system
- Built-in command framework
- Plugin/extension system
- Automatic authentication
- Discord.py adapter
- Clean developer-friendly API

---

# Installation

```bash
pip install craftcord
```

---

# Quick Start

## 1. Configure Environment Variables

```bash
export CRAFTCORD_HOST="127.0.0.1"
export CRAFTCORD_PORT="8080"
export CRAFTCORD_TOKEN="your-api-token"
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

---

## 2. Minimal Example

```python
import asyncio

from craftcord import Client


async def main():
    client = Client(
        host="127.0.0.1",
        port=8080,
        token="secret"
    )

    @client.command("online")
    async def online():
        return [
            player.username
            for player in await client.minecraft.players()
        ]

    await client.start()


asyncio.run(main())
```

---

# Minecraft API

The `client.minecraft` service exposes high-level methods.

## Players

```python
await client.minecraft.players()
await client.minecraft.get_players()
```

## Server Information

```python
await client.minecraft.server_info()
await client.minecraft.get_server_info()
```

## Chat

```python
await client.minecraft.send_message("Hello!")
await client.minecraft.send_message(
    "Welcome!",
    target="Steve"
)
```

## Commands

```python
await client.minecraft.execute("time set day")
```

## Moderation

```python
await client.minecraft.kick("Steve")

await client.minecraft.ban(
    "Steve",
    reason="Griefing"
)
```

---

# Events

Subscribe to real-time Minecraft events.

```python
@client.on("player_join")
async def joined(event):
    print(event.player.username)
```

Built-in events:

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

Extensions can register commands and event listeners.

```python
class GreetingExtension:

    async def setup(self, client):

        @client.on("player_join")
        async def greet(event):

            await client.minecraft.send_message(
                f"Welcome {event.player.username}!"
            )


await client.plugins.load(
    GreetingExtension()
)
```

## Protocol Contract (For Java Plugin Authors)

## Migration Note (Plugin Networking Update)

- New plugin exposure options: `bindMode` (`local|global`) and optional `host` override.
- SDK API contract is unchanged: endpoints remain `/api/v1/auth/validate`, `/api/v1/rpc`, and `/ws`.
- Existing users with explicit SDK host/port configuration continue to work unchanged.
- SDK now rejects `0.0.0.0` as a client target host with a clear validation error.

Expected API behavior:

- Scripts
- Cron jobs
- Simple integrations

```bash
export CRAFTCORD_TRANSPORT=http
```

---

# Troubleshooting

## Connection retries

Verify:

- CraftCordPlugin is running.
- Host and port are correct.
- API token matches.
- Firewall allows the connection.

---

## Discord commands do not respond

If you're using the Discord adapter:

- Enable Message Content Intent.
- Verify bot permissions.
- Check your command prefix.

---

# Protocol

CraftCord communicates using authenticated JSON RPC over HTTP or WebSockets.

Authentication:

- Bearer Token
- HTTP validation endpoint
- WebSocket authentication

Example request:

```json
{
  "type": "request",
  "id": "uuid",
  "action": "minecraft.get_players",
  "payload": {}
}
```

---

# Development

Run tests:

```bash
pytest
```

Run Ruff:

```bash
ruff check .
```

---

# Repository Structure

```
craftcord/
docs/
examples/
tests/
```

---

# License

MIT License.
