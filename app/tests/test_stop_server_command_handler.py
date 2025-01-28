import os
import unittest
from unittest.mock import MagicMock, patch
from src.command.stop_server_command_handler import StopServerCommandHandler


class TestStopServerCommandHandler(unittest.TestCase):

    @patch.dict(os.environ, {"VALHEIM_SERVER_ECS_CLUSTER": "TestCluster", "VALHEIM_SERVER_ECS_SERVICE": "TestService"})
    @patch("boto3.client")
    def test_stop_server_with_running_tasks(self, mock_boto_client):
        mock_ecs_client = MagicMock()
        mock_boto_client.return_value = mock_ecs_client
        mock_ecs_client.describe_services.return_value = {
            "services": [{"runningCount": 1}]
        }

        handler = StopServerCommandHandler()
        response = handler.execute({})

        mock_ecs_client.update_service.assert_called_once_with(
            cluster="TestCluster",
            service="TestService",
            desiredCount=0,
            forceNewDeployment=False,
        )
        self.assertEqual(response, "Server is being stopped. Tasks will be terminated shortly. 🛑")

    @patch.dict(os.environ, {"VALHEIM_SERVER_ECS_CLUSTER": "TestCluster", "VALHEIM_SERVER_ECS_SERVICE": "TestService"})
    @patch("boto3.client")
    def test_stop_server_with_no_running_tasks(self, mock_boto_client):
        mock_ecs_client = MagicMock()
        mock_boto_client.return_value = mock_ecs_client
        mock_ecs_client.describe_services.return_value = {
            "services": [{"runningCount": 0}]
        }

        handler = StopServerCommandHandler()
        response = handler.execute({})

        mock_ecs_client.update_service.assert_not_called()
        self.assertEqual(response, "Server is not online. No action taken. 💤")

    @patch.dict(os.environ, {"VALHEIM_SERVER_ECS_CLUSTER": "TestCluster", "VALHEIM_SERVER_ECS_SERVICE": "TestService"})
    @patch("boto3.client")
    def test_service_not_available(self, mock_boto_client):
        mock_ecs_client = MagicMock()
        mock_boto_client.return_value = mock_ecs_client
        mock_ecs_client.describe_services.return_value = {"services": []}

        handler = StopServerCommandHandler()
        response = handler.execute({})

        mock_ecs_client.update_service.assert_not_called()
        self.assertEqual(response, "An error occurred while stopping the server. Service is not available. ⚠️")

    @patch("boto3.client")
    def test_stop_server_with_exception(self, mock_boto_client):
        mock_ecs_client = MagicMock()
        mock_boto_client.return_value = mock_ecs_client
        mock_ecs_client.describe_services.side_effect = Exception("Some unexpected error")

        handler = StopServerCommandHandler()
        response = handler.execute({})

        mock_ecs_client.update_service.assert_not_called()
        self.assertEqual(response, "An error occurred while stopping the server. Please check the logs for more details. ❗")
