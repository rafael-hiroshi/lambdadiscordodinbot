import logging
import os
from typing import Callable, Dict

from flask import Flask, jsonify, request
from mangum import Mangum
from asgiref.wsgi import WsgiToAsgi
from discord_interactions import verify_key_decorator, InteractionType

from command.echo_command_handler import EchoCommandHandler
from command.hello_command_handler import HelloCommandHandler

DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)
handler = Mangum(asgi_app, lifespan="off")


@app.route("/", methods=["POST"])
def interactions():
    raw_request = request.json
    logger.info(raw_request)
    return interact(raw_request)


def interaction_response(request_body: dict):
    response = {
        "1": InteractionType.PING,
        "2": InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE,
        "4": InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE
    }

    return response[str(request_body["type"])]


def resolve_command(command_name: str) -> Callable[[Dict], str]:
    handlers = {
        "hello": HelloCommandHandler(),
        "echo": EchoCommandHandler()
    }

    command_handler = handlers.get(command_name)
    if not command_handler:
        raise ValueError(f"Command '{command_name}' not found.")

    return command_handler.execute



@verify_key_decorator(DISCORD_PUBLIC_KEY)
def interact(raw_request):
    data = raw_request["data"]
    command_name = data["name"]

    command_func = resolve_command(command_name)
    command_response = command_func(data)

    response_data = {
        "type": interaction_response(raw_request),
        "data": {
            "content": command_response
        },
    }

    logger.info(response_data)
    return jsonify(response_data)


if __name__ == "__main__":
    app.run(debug=True)
