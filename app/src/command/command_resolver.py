from typing import Callable, Dict
from src.command.echo_command_handler import EchoCommandHandler
from src.command.hello_command_handler import HelloCommandHandler


class CommandResolver:

    def __init__(self):
        self.__handlers = {
            "hello": HelloCommandHandler(),
            "echo": EchoCommandHandler()
        }

    def resolve_command(self, command_name: str) -> Callable[[Dict], str]:
        command_handler = self.__handlers.get(command_name)

        if not command_handler:
            raise ValueError(f"Command '{command_name}' not found.")

        return command_handler.execute
