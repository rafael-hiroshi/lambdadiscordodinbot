import json
import logging
from discord_interactions import verify_key_decorator

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # TODO implement
    logger.info(event)
    logger.info("New image")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
