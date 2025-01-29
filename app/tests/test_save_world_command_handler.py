import os
import unittest
from unittest.mock import MagicMock, patch

from src.command.save_world_command_handler import SaveWorldCommandHandler


class TestSaveWorldCommandHandler(unittest.TestCase):

    @patch("boto3.client")
    def test_save_world_no_running_tasks(self, mock_boto_client):
        os.environ["VALHEIM_SERVER_ECS_CLUSTER"] = "test-cluster"
        os.environ["VALHEIM_ECS_SERVICE"] = "test-service"
        os.environ["VALHEIM_CONTAINER_NAME"] = "test-container"

        mock_ecs_client = MagicMock()
        mock_boto_client.return_value = mock_ecs_client
        mock_ecs_client.list_tasks.return_value = {"taskArns": []}

        handler = SaveWorldCommandHandler()
        response = handler.execute({})

        mock_ecs_client.list_tasks.assert_called_once_with(
            cluster="test-cluster", serviceName="test-service", desiredStatus="RUNNING"
        )
        assert response == "No running server tasks were found. Unable to save the world. 🛑"

    @patch("boto3.client")
    def test_save_world_command_executed_successfully(self, mock_boto_client):
        os.environ["VALHEIM_SERVER_ECS_CLUSTER"] = "test-cluster"
        os.environ["VALHEIM_ECS_SERVICE"] = "test-service"
        os.environ["VALHEIM_CONTAINER_NAME"] = "test-container"

        mock_ecs_client = MagicMock()
        mock_boto_client.return_value = mock_ecs_client
        mock_ecs_client.list_tasks.return_value = {"taskArns": ["task-arn-1"]}

        mock_ecs_client.execute_command.return_value = {
            "clusterArn": "test-cluster-arn",
            "taskArn": "task-arn-1",
            "containerName": "test-container",
            "command": "supervisorctl restart valheim-backup",
        }

        handler = SaveWorldCommandHandler()
        response = handler.execute({})

        mock_ecs_client.list_tasks.assert_called_once_with(
            cluster="test-cluster", serviceName="test-service", desiredStatus="RUNNING"
        )
        mock_ecs_client.execute_command.assert_called_once_with(
            cluster="test-cluster",
            task="task-arn-1",
            container="test-container",
            interactive=False,
            command="supervisorctl restart valheim-backup",
        )
        assert response == "World save process has been initiated. 💾"

    @patch("boto3.client")
    def test_save_world_error(self, mock_boto_client):
        os.environ["VALHEIM_SERVER_ECS_CLUSTER"] = "test-cluster"
        os.environ["VALHEIM_ECS_SERVICE"] = "test-service"
        os.environ["VALHEIM_CONTAINER_NAME"] = "test-container"

        mock_ecs_client = MagicMock()
        mock_boto_client.return_value = mock_ecs_client
        mock_ecs_client.list_tasks.side_effect = Exception("Some ECS error")

        handler = SaveWorldCommandHandler()
        response = handler.execute({})

        mock_ecs_client.list_tasks.assert_called_once_with(
            cluster="test-cluster", serviceName="test-service", desiredStatus="RUNNING"
        )
        assert response == "An error occurred while saving the world. Please check the logs for more details."
