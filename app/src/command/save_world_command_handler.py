import logging
import os

import boto3

from src.command.command_handler import CommandHandler

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class SaveWorldCommandHandler(CommandHandler):

    def __init__(self):
        self.__ecs_client = boto3.client("ecs")

    def execute(self, request_data: dict) -> str:
        cluster_name = os.getenv("VALHEIM_SERVER_ECS_CLUSTER")
        service_name = os.getenv("VALHEIM_SERVER_ECS_SERVICE")
        container_name = os.getenv("VALHEIM_CONTAINER_NAME")
        command_to_execute = "supervisorctl restart valheim-backup"

        try:
            tasks_response = self.__ecs_client.list_tasks(
                cluster=cluster_name,
                serviceName=service_name,
                desiredStatus="RUNNING"
            )
            task_arns = tasks_response.get("taskArns", [])

            if not task_arns:
                return "No running server tasks were found. Unable to save the world. 🛑"

            task_arn = task_arns[0]
            response = self.__ecs_client.execute_command(
                cluster=cluster_name,
                task=task_arn,
                container=container_name,
                interactive=True,
                command=command_to_execute,
            )

            logger.info(f"Command executed successfully: {response}")
            return "World save process has been initiated. 💾"
        except Exception as e:
            logger.error(f"Error while saving the world: {str(e)}")
            return "An error occurred while saving the world. Please check the logs for more details."
