import os
import unittest
from unittest.mock import patch, MagicMock

from src.command.start_server_command_handler import StartServerCommandHandler


class TestStartServerCommandHandler(unittest.TestCase):

    @patch.dict(os.environ, {"VALHEIM_SERVER_ECS_CLUSTER": "TestCluster", "VALHEIM_SERVER_ECS_SERVICE": "TestService"})
    @patch("boto3.client")
    def test_server_launching(self, mock_boto_client):
        mock_ecs = MagicMock()
        mock_boto_client.return_value = mock_ecs
        mock_ecs.describe_services.return_value = {
            "services": [{"runningCount": 0, "desiredCount": 0}]
        }

        handler = StartServerCommandHandler()
        response = handler.execute({})

        mock_ecs.update_service.assert_called_once_with(
            cluster="TestCluster",
            service="TestService",
            desiredCount=1,
            forceNewDeployment=True,
        )
        self.assertEqual(response, "Server is about to launch in a few minutes. Hang tight while we get everything set up!")

    @patch.dict(os.environ, {"VALHEIM_SERVER_ECS_CLUSTER": "TestCluster", "VALHEIM_SERVER_ECS_SERVICE": "TestService"})
    @patch("boto3.client")
    def test_server_is_already_running(self, mock_boto_client):
        mock_ecs = MagicMock()
        mock_boto_client.return_value = mock_ecs
        mock_ecs.describe_services.return_value = {
            "services": [{"runningCount": 1, "desiredCount": 1}]
        }

        handler = StartServerCommandHandler()
        response = handler.execute({})

        mock_ecs.update_service.assert_not_called()
        self.assertEqual(response, "Server is already running. No action taken.")

    @patch.dict(os.environ, {"VALHEIM_SERVER_ECS_CLUSTER": "TestCluster", "VALHEIM_SERVER_ECS_SERVICE": "TestService"})
    @patch("boto3.client")
    def test_service_not_available(self, mock_boto_client):
        mock_ecs = MagicMock()
        mock_boto_client.return_value = mock_ecs
        mock_ecs.describe_services.return_value = {"services": []}

        handler = StartServerCommandHandler()
        response = handler.execute({})

        mock_ecs.update_service.assert_not_called()
        self.assertEqual(response, "An error occurred while starting the server. Service is not available.")

    @patch.dict(os.environ, {"VALHEIM_SERVER_ECS_CLUSTER": "TestCluster", "VALHEIM_SERVER_ECS_SERVICE": "TestService"})
    @patch("boto3.client")
    def test_server_error(self, mock_boto_client):
        mock_ecs = MagicMock()
        mock_boto_client.return_value = mock_ecs
        mock_ecs.describe_services.side_effect = Exception("Something went wrong")

        handler = StartServerCommandHandler()
        response = handler.execute({})

        mock_ecs.update_service.assert_not_called()
        self.assertEqual(response, "An error occurred while starting the server. Please check the logs for more details.")
