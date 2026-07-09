# CraftCord Documentation

CraftCord is a transport-focused Python SDK that sits between your application and a separate Java CraftCord plugin running beside a Minecraft server.

## Design Goals

- make server automation feel native to Python developers
- keep transport and protocol concerns isolated from higher-level application code
- provide reliable reconnect and timeout behavior for long-running bots
- stay framework-agnostic for Discord integrations

## Core Concepts

- `Client`: top-level orchestration object for transports, events, commands, and adapters
- `MinecraftClient`: high-level methods for server actions such as command execution and player lookups
- `Transport`: protocol boundary for WebSocket and HTTP communication with the Java plugin
- `DiscordAdapter`: bridge to Discord frameworks without coupling CraftCord to a specific bot runtime
- `PluginManager`: Python-side extension lifecycle manager

See the API reference in `docs/api.md` and the repository root `README.md` for setup examples.
