from __future__ import annotations

import asyncio

from craftcord import Client
from craftcord.transport.http import HTTPTransport


async def main() -> None:
    client = Client(
        host="localhost",
        port=8080,
        token="secret",
        transport=HTTPTransport,
    )

    await client.connect()
    info = await client.minecraft.get_server_info()
    print(info)
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
