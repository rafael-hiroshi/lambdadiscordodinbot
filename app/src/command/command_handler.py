from abc import ABC, abstractmethod


class CommandHandler(ABC):

    @abstractmethod
    def execute(self, request_body: dict) -> str:
        pass
