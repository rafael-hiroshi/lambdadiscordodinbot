import json

from lambda_function import app
from discord_interactions import InteractionType, InteractionResponseType


def test_interactions():

    with app.test_client() as client:
        request_data = {
            "type": InteractionType.APPLICATION_COMMAND,
            "data": {
                "name": "hello"
            }
        }

        response = client.post(
            "/",
            data=json.dumps(request_data),
            content_type="application/json"
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)

        assert response_data["type"] == InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE
        assert response_data["data"]["content"] == "Hello there!"
