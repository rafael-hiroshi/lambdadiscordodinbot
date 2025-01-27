import json
import logging
import os

from asgiref.wsgi import WsgiToAsgi
from discord_interactions import verify_key_decorator, InteractionType, InteractionResponseType
from flask import Flask, jsonify, request
from mangum import Mangum

from src.command.command_resolver import CommandResolver

DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)
handler = Mangum(asgi_app, lifespan="off")


@verify_key_decorator(DISCORD_PUBLIC_KEY)
@app.route("/", methods=["POST"])
def interactions():
    raw_request = request.json
    data = raw_request["data"]
    command_handler = CommandResolver().resolve_command(data["name"])
    command_response = command_handler.execute(data)

    response_data = {
        "type": interaction_response(raw_request["type"]),
        "data": {
            "content": command_response
        },
    }

    logger.info(json.dumps(response_data))
    return jsonify(response_data)


def interaction_response(request_type: int):
    response = {
        f"{InteractionType.PING}": InteractionResponseType.PONG,
        f"{InteractionType.APPLICATION_COMMAND}": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
        f"{InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE}": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE
    }

    return response[str(request_type)]
