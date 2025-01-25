from command.abstract_command import Command


class HelloCommandHandler(Command):

    def execute(self, request_data: dict) -> str:
        return "Hello there!"
