from command.abstract_command import Command


class EchoCommandHandler(Command):

    def execute(self, request_data: dict) -> str:
        original_message = request_data["options"][0]["value"]
        return f"Echoing: {original_message}"
