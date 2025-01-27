import logging
import os

import boto3

from src.command.command_handler import CommandHandler

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class StopServerCommandHandler(CommandHandler):
    def __init__(self):
        self.__ecs_client = boto3.client("ecs")

    def execute(self, request_data: dict) -> str:
        cluster_name = os.getenv("VALHEIM_SERVER_ECS_CLUSTER")
        service_name = os.getenv("VALHEIM_ECS_SERVICE")

        try:
            response = self.__ecs_client.describe_services(cluster=cluster_name, services=[service_name])
            services = response.get("services", [])

            if not services:
                return f"An error occurred while stopping the server. Service is not available."

            service = services[0]
            running_count = service.get("runningCount", 0)

            if running_count == 0:
                return f"Server is not online. No action taken."

            self.__ecs_client.update_service(
                cluster=cluster_name,
                service=service_name,
                desiredCount=0,
                forceNewDeployment=False,
            )

            return "Server is being stopped. Tasks will be terminated shortly."
        except Exception as e:
            logger.error(f"Error while stopping the server: {str(e)}")
            return "An error occurred while stopping the server. Please check the logs for more details."
