from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, kw_only=True)
class ClientConfig:
    host: str
    port: int
    token: str
    secure: bool = False
    websocket_path: str = "/ws"
    http_base_path: str = "/api/v1"
    connect_timeout: float = 10.0
    request_timeout: float = 10.0
    heartbeat_interval: float = 20.0
    reconnect: bool = True
    reconnect_backoff: float = 1.0
    reconnect_max_backoff: float = 30.0
    user_agent: str = "craftcord/0.1.0"
    headers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.host = self.host.strip()
        if not self.host:
            raise ValueError("host must be a non-empty hostname or IP address")
        if self.host == "0.0.0.0":
            raise ValueError(
                "Invalid client host '0.0.0.0': use a reachable plugin address "
                "such as 127.0.0.1, a LAN IP, or a DNS hostname."
            )

    @property
    def ws_url(self) -> str:
        scheme = "wss" if self.secure else "ws"
        return f"{scheme}://{self.host}:{self.port}{self.websocket_path}"

    @property
    def http_url(self) -> str:
        scheme = "https" if self.secure else "http"
        return f"{scheme}://{self.host}:{self.port}{self.http_base_path}"
