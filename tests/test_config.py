from __future__ import annotations

import pytest

from craftcord.core.config import ClientConfig


def test_client_config_rejects_wildcard_bind_host() -> None:
    with pytest.raises(ValueError, match="0\\.0\\.0\\.0"):
        ClientConfig(host="0.0.0.0", port=8080, token="secret")


def test_client_config_accepts_explicit_host_for_urls() -> None:
    config = ClientConfig(host="192.168.1.50", port=8080, token="secret")

    assert config.http_url == "http://192.168.1.50:8080/api/v1"
    assert config.ws_url == "ws://192.168.1.50:8080/ws"
