# CraftCord Documentation

CraftCord is a transport-focused Python SDK that sits between your application and a separate Java CraftCord plugin running beside a Minecraft server.

## Design Goals

- make server automation feel native to Python developers
- keep transport and protocol concerns isolated from higher-level application code
- provide reliable reconnect and timeout behavior for long-running bots
- stay framework-agnostic for Discord integrations

## Core Concepts

- `Client`: top-level orchestration object for transports, events, and commands
- `MinecraftClient`: high-level methods for server actions such as command execution and player lookups
- `Transport`: protocol boundary for WebSocket and HTTP communication with the Java plugin
- `PluginManager`: Python-side extension lifecycle manager

See the API reference in `docs/api.md` and the repository root `README.md` for setup examples.

## Local vs Global Plugin Exposure

The Java plugin now controls bind behavior through:

- `bindMode=local` (binds to `127.0.0.1`)
- `bindMode=global` (binds to `0.0.0.0`)
- optional non-empty `host` (overrides bind mode with a specific interface)

This does not change endpoint paths; SDK requests still use `/api/v1/*` and `/ws`.

Client connection targets must be reachable:

- local process on same machine: `http://127.0.0.1:8080/api/v1`
- LAN client: `http://<server-lan-ip>:8080/api/v1`
- reverse proxy/public: `https://craftcord.example.com/api/v1`

Do not use `0.0.0.0` as a client target host.

## Troubleshooting Connectivity

For `connection refused` or timeout errors:

1. Verify plugin `bindMode` and optional `host` config.
2. Confirm SDK host points to a reachable IP/hostname for the client machine.
3. Verify token, port, and transport selection.
4. Check host firewall, cloud security groups, and LAN routing.
5. For external access, verify NAT/port-forwarding and reverse-proxy upstream routes.
