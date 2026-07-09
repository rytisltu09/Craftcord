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

If you're using the Discord.py adapter, also configure:

```bash
export DISCORD_TOKEN="your-discord-token"
```

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

- player_join
- player_leave
- player_chat
- player_death
- server_start
- server_stop

Unknown events are delivered as `GenericEvent`.

---

# Commands

CraftCord provides its own command framework.

```python
@client.command("online")
async def online():
    ...
```

This allows business logic to remain independent of Discord or any other frontend.

For example:

Discord command

↓

CraftCord command

↓

Minecraft

---

# Plugin System

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

---

# Transport

CraftCord supports two transport protocols.

## WebSocket

Recommended for:

- Discord bots
- Dashboards
- Live monitoring
- Event-driven applications

```bash
export CRAFTCORD_TRANSPORT=ws
```

## HTTP

Recommended for:

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
