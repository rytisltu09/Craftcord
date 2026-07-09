# Example of a basic CraftCord bot that bridges Minecraft and Discord.

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

import discord
from discord.ext import commands
from dotenv import load_dotenv

from craftcord import Client
from craftcord.core.config import ClientConfig
from craftcord.core.events import BaseEvent, GenericEvent
from craftcord.discord.discordpy import DiscordPyAdapter
from craftcord.minecraft.events import PlayerChatEvent, PlayerJoinEvent
from craftcord.minecraft.models import ServerInfo
from craftcord.transport.http import HTTPTransport

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("craftcord.examples.basic_bot")


load_dotenv("basic_bot.env")
CRAFTCORD_DEFAULT_CHANNEL = os.getenv("CRAFTCORD_DEFAULT_CHANNEL")
CRAFTCORD_HOST = os.getenv("CRAFTCORD_HOST", "localhost")
CRAFTCORD_PORT = int(os.getenv("CRAFTCORD_PORT", "25565"))
CRAFTCORD_TOKEN = os.getenv("CRAFTCORD_TOKEN")
CRAFTCORD_TRANSPORT = os.getenv("CRAFTCORD_TRANSPORT", "ws")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)


async def _discord_command_responder(command_name: str, result: Any) -> None:
    if CRAFTCORD_DEFAULT_CHANNEL is None:
        return
    await craft.discord.send(f"command `{command_name}` result: {result}")


async def _discord_event_forwarder(event: BaseEvent) -> None:
    if CRAFTCORD_DEFAULT_CHANNEL is None:
        return

    if isinstance(event, PlayerJoinEvent):
        await craft.discord.send(f"{event.player.username} joined Minecraft")
        return
    if isinstance(event, PlayerChatEvent):
        await craft.discord.send(f"<{event.player.username}> {event.message}")
        return

    await craft.discord.send(f"minecraft event: {event.name}")


adapter = DiscordPyAdapter(
    bot,
    default_channel=int(CRAFTCORD_DEFAULT_CHANNEL) if CRAFTCORD_DEFAULT_CHANNEL else None,
    command_responder=_discord_command_responder,
    event_forwarder=_discord_event_forwarder,
)

config = ClientConfig(
    host=CRAFTCORD_HOST,
    port=CRAFTCORD_PORT,
    token=CRAFTCORD_TOKEN,
    headers={"X-CraftCord-Example": "basic-bot"},
)

transport = HTTPTransport if CRAFTCORD_TRANSPORT == "http" else None

craft = Client(
    host=CRAFTCORD_HOST,
    port=CRAFTCORD_PORT,
    token=CRAFTCORD_TOKEN,
    transport=transport,
    discord_adapter=adapter,
    config=config,
)


class JoinAnnouncerPlugin:
    def __init__(self) -> None:
        self._listener: Any = None

    async def setup(self, client: Client) -> None:
        async def announce_join(event: PlayerJoinEvent) -> None:
            await client.minecraft.send_message(f"Welcome {event.player.username}!")

        self._listener = announce_join
        client.on("player_join")(announce_join)

    async def teardown(self, client: Client) -> None:
        if self._listener is not None:
            client.remove_listener("player_join", self._listener)


plugin_manager = craft.plugins


@craft.event("player_join")
async def on_player_join(event: PlayerJoinEvent) -> None:
    logger.info("player joined: %s", event.player.username)


@craft.event("player_chat")
async def on_player_chat(event: PlayerChatEvent) -> None:
    if event.message.strip().lower() == "!discord":
        await craft.minecraft.send_message(
            "Discord bridge is online.",
            target=event.player.username,
        )


@craft.on("*")
async def on_any_event(event: BaseEvent) -> None:
    if isinstance(event, GenericEvent):
        logger.info("generic event %s payload=%s", event.name, event.data)


@craft.command("online")
async def online_players() -> list[str]:
    players = await craft.minecraft.players()
    return [player.username for player in players]


@craft.command("server")
async def server_info() -> dict[str, Any]:
    info: ServerInfo = await craft.minecraft.server_info()
    return {
        "version": info.version,
        "online_players": info.online_players,
        "max_players": info.max_players,
        "uptime": info.uptime,
    }

@craft.command("say")
async def say_to_minecraft(message: str) -> str:
    await craft.minecraft.send_message(message)
    return "message sent"


@craft.command("execute")
async def execute_minecraft(command: str) -> dict[str, Any]:
    return await craft.minecraft.execute(command)


@craft.command("kick")
async def kick_player(username: str, reason: str | None = None) -> str:
    await craft.minecraft.kick(username, reason=reason)
    return f"kicked {username}"


@craft.command("ban")
async def ban_player(username: str, reason: str | None = None) -> str:
    await craft.minecraft.ban(username, reason=reason)
    return f"banned {username}"


@bot.event
async def on_ready() -> None:
    logger.info(
        "logged in as %s (%s)",
        bot.user.name if bot.user else "unknown",
        bot.user.id if bot.user else "unknown",
    )
    logger.info("selected transport: %s", "http" if transport is HTTPTransport else "websocket")

    await craft.connect()

    if "JoinAnnouncerPlugin" not in plugin_manager.loaded:
        await plugin_manager.load(JoinAnnouncerPlugin)


@bot.command(name="ping")
async def ping(ctx: commands.Context[commands.Bot]) -> None:
    await ctx.send("Pong!")


@bot.command(name="mc_online")
async def mc_online(ctx: commands.Context[commands.Bot]) -> None:
    result = await craft.invoke_command("online")
    await ctx.send(f"Online players: {', '.join(result) if result else 'none'}")


@bot.command(name="mc_server")
async def mc_server(ctx: commands.Context[commands.Bot]) -> None:
    result = await craft.invoke_command("server")
    await ctx.send(
        "Server "
        f"v{result['version']} "
        f"players={result['online_players']}/{result['max_players']} "
        f"uptime={result['uptime']:.1f}s"
    )


@bot.command(name="mc_say")
async def mc_say(ctx: commands.Context[commands.Bot], *, message: str) -> None:
    await craft.invoke_command("say", message)
    await ctx.send("Sent")


@bot.command(name="mc_exec")
async def mc_exec(ctx: commands.Context[commands.Bot], *, command: str) -> None:
    result = await craft.invoke_command("execute", command)
    await ctx.send(f"Execute result: {result}")


@bot.command(name="mc_kick")
async def mc_kick(
    ctx: commands.Context[commands.Bot],
    username: str,
    *,
    reason: str | None = None,
) -> None:
    await craft.invoke_command("kick", username, reason)
    await ctx.send(f"Kicked {username}")


@bot.command(name="mc_ban")
async def mc_ban(
    ctx: commands.Context[commands.Bot],
    username: str,
    *,
    reason: str | None = None,
) -> None:
    await craft.invoke_command("ban", username, reason)
    await ctx.send(f"Banned {username}")


@bot.command(name="mc_raw")
async def mc_raw(
    ctx: commands.Context[commands.Bot],
    action: str,
    *,
    payload_json: str = "{}",
) -> None:
    payload = json.loads(payload_json)
    result = await craft.request(action, payload)
    await ctx.send(f"Raw result: {result}")


@bot.command(name="plugin_unload")
async def plugin_unload(
    ctx: commands.Context[commands.Bot],
    name: str = "JoinAnnouncerPlugin",
) -> None:
    unloaded = await plugin_manager.unload(name)
    await ctx.send("Plugin unloaded" if unloaded else "Plugin was not loaded")


@bot.command(name="plugin_load")
async def plugin_load(ctx: commands.Context[commands.Bot]) -> None:
    if "JoinAnnouncerPlugin" in plugin_manager.loaded:
        await ctx.send("Plugin already loaded")
        return
    await plugin_manager.load(JoinAnnouncerPlugin)
    await ctx.send("Plugin loaded")


@bot.command(name="craftcord_close")
async def craftcord_close(ctx: commands.Context[commands.Bot]) -> None:
    await craft.close()
    await ctx.send("CraftCord client closed")


async def main() -> None:
    if DISCORD_TOKEN is None:
        raise RuntimeError("Missing DISCORD_TOKEN environment variable")

    try:
        await bot.start(DISCORD_TOKEN)
    finally:
        await craft.close()


if __name__ == "__main__":
    asyncio.run(main())