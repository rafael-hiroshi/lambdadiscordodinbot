from src.command.command_handler import CommandHandler


class HelloCommandHandler(CommandHandler):

    def execute(self, request_data: dict) -> str:
        return "Hello there!"
