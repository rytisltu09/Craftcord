from __future__ import annotations

from craftcord.client import Client
from craftcord.core.config import ClientConfig
from craftcord.transport.http import HTTPTransport


def test_client_accepts_transport_factory() -> None:
    client = Client(
        host="127.0.0.1",
        port=8080,
        token="secret",
        transport=HTTPTransport,
    )

    assert isinstance(client.transport, HTTPTransport)
    assert client.transport.config == ClientConfig(host="127.0.0.1", port=8080, token="secret")