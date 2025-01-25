from src.command.command_handler import CommandHandler


class EchoCommandHandler(CommandHandler):

    def execute(self, request_data: dict) -> str:
        original_message = request_data["options"][0]["value"]
        return f"Echoing: {original_message}"
