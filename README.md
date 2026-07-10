# CraftCord

**CraftCord** is an asynchronous Python SDK for communicating with Minecraft Paper servers through **CraftCordPlugin**.

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
- `discord.py` adapter
- Clean, developer-friendly API

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

---

## Local vs Global Plugin Exposure

CraftCordPlugin supports different network exposure modes.

### Plugin Configuration

The Java plugin controls how it binds to the network:

- `bindMode=local` → binds to `127.0.0.1` (localhost only)
- `bindMode=global` → binds to `0.0.0.0` (all interfaces)
- `host=<ip-or-hostname>` → overrides `bindMode` and binds to a specific interface

### SDK Connection Guidance

Your Python application should always connect to a **reachable address**.

> **Do not use `0.0.0.0` as `CRAFTCORD_HOST`.**
>
> `0.0.0.0` is a server bind address, **not** a valid client destination.

Example connection URLs:

| Deployment | URL |
|------------|-----|
| Same machine | `http://127.0.0.1:8080/api/v1` |
| Local network | `http://<server-lan-ip>:8080/api/v1` |
| Public / Reverse Proxy | `https://craftcord.example.com/api/v1` |

When the plugin starts, it logs whether it is running in:

- Local-only mode
- Global mode
- Specific-interface mode

allowing you to verify the network configuration immediately.

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
        players = await client.minecraft.players()
        return [player.username for player in players]

    await client.start()


asyncio.run(main())
```

---

# Minecraft API

The `client.minecraft` service exposes several high-level methods.

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

Subscribe to live Minecraft events.

```python
@client.on("player_join")
async def joined(event):
    print(event.player.username)
```

Built-in events include:

- `player_join`
- `player_leave`
- `player_chat`
- `player_death`
- `server_start`
- `server_stop`

Unknown events are delivered as `GenericEvent`.

---

# Transport Choice

CraftCord supports two transport methods.

## WebSocket (`ws`)

Recommended for:

- Discord bots
- Dashboards
- Monitoring applications
- Real-time event streaming

```bash
export CRAFTCORD_TRANSPORT="ws"
```

## HTTP (`http`)

Recommended for:

- Scripts
- Cron jobs
- One-off integrations
- Request/response applications

```bash
export CRAFTCORD_TRANSPORT="http"
```

---

# Troubleshooting

## Connection Refused or Timeout

Verify the following:

1. The Java plugin is running.
2. `bindMode` and `host` are configured correctly.
3. `CRAFTCORD_HOST` points to a reachable address.
4. **Never** use `0.0.0.0` as the SDK host.
5. `CRAFTCORD_PORT` matches the plugin configuration.
6. `CRAFTCORD_TOKEN` matches the plugin configuration.
7. Firewall rules allow inbound connections.
8. If accessing remotely, verify routing and port forwarding.
9. If using a reverse proxy, ensure `/api/v1/*` and `/ws` are forwarded correctly.

---

## WebSocket Keeps Reconnecting

This usually means the SDK cannot reach the CraftCordPlugin.

Check:

- Is the plugin running?
- Are the host and port correct?
- Does the API token match?
- Is WebSocket enabled?
- If the server only exposes HTTP, set:

```bash
export CRAFTCORD_TRANSPORT="http"
```

---

## Discord Commands Don't Work

If you're using the built-in `discord.py` adapter:

- Enable the **Message Content Intent**.
- Ensure the bot has permission to read and send messages.
- Verify your command prefix.

---

## Python 3.14 Compatibility

If you encounter dataclass or import issues, update to the latest version of CraftCord.

Recent releases include Python 3.14 compatibility improvements.

---

# Plugin System

Extensions allow reusable commands and event listeners.

```python
class GreetingExtension:

    async def setup(self, client):

        @client.on("player_join")
        async def greet(event):

            await client.minecraft.send_message(
                f"Welcome {event.player.username}!"
            )


await client.plugins.load(GreetingExtension())
```

---

# Protocol Contract

## Migration Notes

Recent versions introduce improved network binding.

### Plugin Changes

- Added `bindMode` (`local` or `global`)
- Added optional `host` override

### SDK Changes

The SDK API remains unchanged.

Endpoints are still:

- `/api/v1/auth/validate`
- `/api/v1/rpc`
- `/ws`

Existing applications continue working without modification.

The SDK now validates `CRAFTCORD_HOST` and rejects `0.0.0.0` as an invalid destination.

---

## Protocol

CraftCord communicates using authenticated JSON-RPC over HTTP and WebSockets.

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

```text
craftcord/
├── docs/
├── examples/
└── tests/
```

---

# License

This project is licensed under the **MIT License**.
