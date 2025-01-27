from src.command.command_handler import CommandHandler
from src.command.echo_command_handler import EchoCommandHandler
from src.command.hello_command_handler import HelloCommandHandler
from src.command.start_server_command_handler import StartServerCommandHandler
from src.command.stop_server_command_handler import StopServerCommandHandler


class CommandResolver:

    def __init__(self):
        self.__handlers = {
            "hello": HelloCommandHandler,
            "echo": EchoCommandHandler,
            "start-server": StartServerCommandHandler,
            "stop-server": StopServerCommandHandler,
        }

    def resolve_command(self, command_name: str) -> CommandHandler:
        command_handler = self.__handlers.get(command_name)

        if not command_handler:
            raise ValueError(f"Command '{command_name}' not found.")

        return command_handler()
