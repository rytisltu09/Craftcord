class CraftCordError(Exception):
    pass


class TransportError(CraftCordError):
    pass


class AuthenticationError(TransportError):
    pass


class ConnectionClosedError(TransportError):
    pass


class RequestTimeoutError(TransportError):
    pass


class ProtocolError(TransportError):
    pass


class CommandNotFoundError(CraftCordError):
    def __init__(self, command_name: str) -> None:
        super().__init__(f"Command '{command_name}' is not registered")
        self.command_name = command_name


class PluginError(CraftCordError):
    pass
