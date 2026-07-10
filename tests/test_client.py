from __future__ import annotations

import pytest

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


def test_client_accepts_explicit_host_unchanged() -> None:
    client = Client(
        host="mc.example.internal",
        port=8080,
        token="secret",
    )

    assert client.config.host == "mc.example.internal"
    assert client.config.http_url == "http://mc.example.internal:8080/api/v1"


def test_client_rejects_wildcard_bind_host() -> None:
    with pytest.raises(ValueError, match="0\\.0\\.0\\.0"):
        Client(host="0.0.0.0", port=8080, token="secret")